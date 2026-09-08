"""CLI orchestration for perturbation-to-human-recovery recording."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from trackmaniarl.commands.evaluation import _load_checkpoint
from trackmaniarl.commands.helpers import _file_sha256
from trackmaniarl.core.contracts import FeaturePipeline, Policy, PolicyMode
from trackmaniarl.core.runtime import ResolvedRun, resolve_run
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.trackmania.environment import OpenPlanetEnvironment, OpenPlanetEnvironmentFactory
from trackmaniarl.trackmania.human_recovery import (
    HumanRecoveryEpisodePlan,
    HumanRecoveryRecordingConfig,
    HumanRecoveryRecordingRequest,
    RecoveryAttemptError,
    RecoveryDemonstration,
    record_human_recovery_episode,
    save_recovery_demonstration,
)
from trackmaniarl.trackmania.human_recovery_plans import (
    resample_human_recovery_plan,
    sample_human_recovery_plans,
)


@dataclass(frozen=True, slots=True)
class _CollectionRuntime:
    args: argparse.Namespace
    environment: OpenPlanetEnvironment
    policy: Policy
    feature_pipeline: FeaturePipeline
    checkpoint_path: Path
    seed: int


@dataclass(frozen=True, slots=True)
class _AttemptSession:
    args: argparse.Namespace
    request: HumanRecoveryRecordingRequest
    plans: list[HumanRecoveryEpisodePlan]
    generator: np.random.Generator
    output: Path


@dataclass(slots=True)
class _AttemptProgress:
    attempt: int
    maximum: int
    completed: int = 0


def _record_human_recovery(args: argparse.Namespace) -> None:
    """Collect completed recovery laps without treating the injected action as expert data."""

    _validate_arguments(args)
    config_path = args.config.resolve()
    spec = _collection_spec(RunSpec.from_yaml(config_path))
    run = resolve_run(spec, base_dir=config_path.parent)
    runtime = None
    try:
        runtime = _collection_runtime(args, spec, run)
        _prewarm_policy(runtime)
        _collect_session(runtime)
    finally:
        if runtime is not None:
            runtime.environment.close()
        run.logger.close()


def _collection_runtime(
    args: argparse.Namespace, spec: RunSpec, run: ResolvedRun
) -> _CollectionRuntime:
    factory = run.environment_factory
    if not isinstance(factory, OpenPlanetEnvironmentFactory):
        raise ValueError("record-recovery requires OpenPlanetEnvironmentFactory")
    checkpoint_path = args.checkpoint.resolve()
    _load_checkpoint(run, checkpoint_path)
    seed = _collection_seed(args, spec)
    policy = run.learner.policy()
    environment = factory.create(seed=seed)
    return _CollectionRuntime(
        args,
        environment,
        policy,
        run.feature_pipeline,
        checkpoint_path,
        seed,
    )


def _collection_spec(spec: RunSpec) -> RunSpec:
    """Disable remote trackers; recovery collection is a local data operation."""

    components = spec.components.model_copy(update={"additional_loggers": ()})
    return spec.model_copy(update={"components": components})


def _prewarm_policy(runtime: _CollectionRuntime) -> None:
    """Pay one-time device initialization before the first recorded model lap."""

    print("Prewarming deterministic evaluation policy before recovery collection.")
    observation, _ = runtime.environment.reset(seed=runtime.seed)
    for component in (runtime.feature_pipeline, runtime.policy):
        reset = getattr(component, "reset_episode", None)
        if callable(reset):
            reset()
    prepared = runtime.feature_pipeline.transform_observation(observation)
    runtime.policy.act(prepared, PolicyMode.EVALUATION)


def _collect_session(runtime: _CollectionRuntime) -> None:
    session = _attempt_session(runtime)
    _collection_intro(session.request.config, runtime.args.count, session.output)
    completed = _collect_attempts(session)
    if completed != runtime.args.count:
        raise RuntimeError(
            f"recorded {completed}/{runtime.args.count} recovery laps before max attempts; "
            "rerun the command to collect the remainder"
        )


def _attempt_session(runtime: _CollectionRuntime) -> _AttemptSession:
    output = runtime.args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    request = HumanRecoveryRecordingRequest(
        environment=runtime.environment,
        policy=runtime.policy,
        feature_pipeline=runtime.feature_pipeline,
        checkpoint_sha256=_file_sha256(runtime.checkpoint_path),
        config=_recording_config(runtime.args),
        status=_collection_status,
    )
    generator = np.random.default_rng(runtime.seed)
    plans = list(sample_human_recovery_plans(request.config, generator, runtime.args.count))
    return _AttemptSession(runtime.args, request, plans, generator, output)


def _recording_config(args: argparse.Namespace) -> HumanRecoveryRecordingConfig:
    return HumanRecoveryRecordingConfig(
        target_progress_min=args.target_progress_min,
        target_progress_max=args.target_progress_max,
        perturbation_duration_min_ms=args.perturbation_duration_min_ms,
        perturbation_duration_max_ms=args.perturbation_duration_max_ms,
        max_duration_s=args.max_duration,
        minimum_context_s=args.minimum_context,
        takeover_timeout_s=args.takeover_timeout,
        human_input_deadzone=args.human_input_deadzone,
    )


def _collection_status(message: str) -> None:
    print(message, flush=True)
    if not message.startswith("TAKE OVER NOW"):
        return
    try:
        import winsound
    except ImportError:
        return
    try:
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
    except RuntimeError:
        return


def _collect_attempts(session: _AttemptSession) -> int:
    args = session.args
    maximum = args.max_attempts or max(args.count * 3, args.count + 2)
    progress = _AttemptProgress(0, maximum)
    for progress.attempt in range(1, maximum + 1):
        if progress.completed >= args.count:
            break
        progress.completed += int(_collect_attempt(session, progress))
    return progress.completed


def _collect_attempt(session: _AttemptSession, progress: _AttemptProgress) -> bool:
    plan = session.plans[progress.completed]
    print(
        f"Recovery attempt {progress.attempt}/{progress.maximum}: "
        f"target={plan.target_progress:.1%}, duration={plan.perturbation_duration_ms:.0f}ms."
    )
    try:
        recovery = record_human_recovery_episode(session.request, plan)
    except (RecoveryAttemptError, TimeoutError, ConnectionError) as error:
        print(f"Discarded attempt {progress.attempt}: {error}")
        session.plans[progress.completed] = resample_human_recovery_plan(
            session.request.config, session.generator, plan
        )
        return False
    _save_attempt(session, recovery, progress.completed + 1)
    return True


def _save_attempt(session: _AttemptSession, recovery: RecoveryDemonstration, rank: int) -> None:
    path = _recovery_output_path(session.output, rank, recovery.demonstration.finish_time_s)
    saved = save_recovery_demonstration(path, recovery)
    print(
        f"Saved recovery {rank}/{session.args.count}: {saved} "
        f"(expert labels begin at step {recovery.takeover_step})."
    )


def _collection_intro(config: HumanRecoveryRecordingConfig, count: int, output: Path) -> None:
    print(
        f"Collecting {count} completed human-recovery laps into {output}. "
        f"The checkpoint drives deterministically to a random "
        f"{config.target_progress_min:.0%}-{config.target_progress_max:.0%} target."
    )
    print(
        "Do not steer before the TAKE OVER NOW message. At takeover, use your human "
        "controls to recover and finish. The first clear input starts expert labels; "
        "forced and reaction-delay frames remain context only."
    )


def _recovery_output_path(output: Path, rank: int, finish_time_s: float) -> Path:
    stem = f"human-recovery-{rank:03d}-{finish_time_s:.3f}s"
    candidate = output / f"{stem}.npz"
    revision = 1
    while candidate.exists():
        revision += 1
        candidate = output / f"{stem}-r{revision}.npz"
    return candidate


def _collection_seed(args: argparse.Namespace, spec: RunSpec) -> int:
    if args.seed is not None:
        return int(args.seed)
    return spec.seed


def _validate_arguments(args: argparse.Namespace) -> None:
    if args.count < 1:
        raise ValueError("recovery count must be positive")
    if args.max_attempts is not None and args.max_attempts < args.count:
        raise ValueError("max attempts must be at least the requested recovery count")
    if not args.checkpoint.is_file():
        raise FileNotFoundError(f"checkpoint does not exist: {args.checkpoint}")
