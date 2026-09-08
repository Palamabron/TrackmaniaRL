"""Reproducible offline screening and live benchmarks of sub37 hypotheses.

Run as ``uv run python -m experiments.sub37.runner --help`` from the repository.
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch

from experiments.sub37.neighbors import NeighborPolicy
from experiments.sub37.policy import (
    EXPERIMENTS,
    Sub37Policy,
    build_envelope,
    reference_episodes,
    replay_columns,
)
from trackmaniarl.commands.evaluation import (
    _apply_benchmark_gate,
    _artifact_trials,
    _load_checkpoint,
    _load_evaluation_artifact,
    _print_benchmark_report,
)
from trackmaniarl.commands.helpers import _file_sha256
from trackmaniarl.core.runtime import resolve_run
from trackmaniarl.core.spec import EvaluationSuiteSpec, RunSpec


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("mode", choices=("offline", "benchmark"))
    result.add_argument("--variant", choices=tuple(EXPERIMENTS), default="baseline")
    result.add_argument("--config", type=Path, required=True)
    result.add_argument("--checkpoint", type=Path, required=True)
    result.add_argument("--trials", type=int, default=10)
    result.add_argument("--start-race-time-ms", type=float)
    return result


def experiment_spec(args: argparse.Namespace) -> RunSpec:
    spec = RunSpec.from_yaml(args.config)
    spec = aligned_start_spec(spec, args.start_race_time_ms)
    if spec.evaluation is None or args.trials < 1:
        raise ValueError("a configured evaluation suite and positive trial count are required")
    evaluation = EvaluationSuiteSpec.model_validate(
        {
            **spec.evaluation.model_dump(),
            "trials_per_map": args.trials,
            "target_mean_s": 37.0,
            "target_median_s": 37.0,
            "min_finish_rate": 1.0,
            "max_step_race_time_ms": 100.0,
            "reject_telemetry_skips": False,
        }
    )
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
    return spec.model_copy(
        update={
            "run_id": f"sub37-v108-{args.mode}-{args.variant}-{stamp}",
            "evaluation": evaluation,
            "components": spec.components.model_copy(update={"additional_loggers": ()}),
        }
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def aligned_start_spec(spec: RunSpec, start_ms: float | None) -> RunSpec:
    if start_ms is None:
        return spec
    environment = spec.components.environment
    if environment is None:
        raise ValueError("aligned start requires a Trackmania environment")
    config = {**environment.kwargs["config"], "start_race_time_ms": start_ms, "start_poll_s": 0.0}
    environment = environment.model_copy(
        update={"kwargs": {**environment.kwargs, "config": config}}
    )
    components = spec.components.model_copy(update={"environment": environment})
    return spec.model_copy(update={"components": components})


def envelope_holdout(replay: dict[str, Any]) -> dict[str, int]:
    columns = replay_columns(replay)
    counts = {"samples": 0, "excluded_actions": 0}
    for rows in reference_episodes(replay):
        code = int(replay["episode_codes"][rows[0]])
        names = {key: value for key, value in replay["episode_names"].items() if key != code}
        mask = build_envelope({**replay, "episode_names": names}).numpy()
        progress = columns["physics"][rows, 3]
        selected = rows[(progress >= 0.54) & (progress < 0.90)]
        bins = (columns["physics"][selected, 3] * 200).astype(int)
        actions = replay["actions"]["arrays"][0][selected].reshape(-1)
        counts["samples"] += len(selected)
        counts["excluded_actions"] += int((~mask[bins, actions]).sum())
    return counts


def offline_screen(policy: Sub37Policy, replay: dict[str, Any]) -> dict[str, Any]:
    if type(policy.base.model.temporal).__name__ != "IdentityTemporalCore":
        raise ValueError("strided offline screening requires IdentityTemporalCore")
    columns = replay_columns(replay)
    codes = replay["episode_codes"]
    references = reference_episodes(replay)
    fast_codes = {int(codes[rows[0]]) for rows in references}
    # Equal sampling stride for every online episode, including failures.
    report: dict[str, Any] = {}
    for name, experiment in EXPERIMENTS.items():
        wrapper_type = NeighborPolicy if "neighbors" in name else Sub37Policy
        policy = wrapper_type(policy.base, experiment, policy.envelope)
        if isinstance(policy, NeighborPolicy):
            policy.configure_references(replay)
        groups = {
            "reference": {"samples": 0, "changed": 0},
            "other_online": {"samples": 0, "changed": 0},
        }
        for code, episode_name in replay["episode_names"].items():
            if episode_name.startswith("demo-"):
                continue
            policy.reset_episode()
            group = groups["reference" if code in fast_codes else "other_online"]
            for row in np.flatnonzero(codes == code)[::20]:
                observation = {key: torch.as_tensor(value[row]) for key, value in columns.items()}
                before = policy.current["changed"] + policy.current.get("neighbor_changes", 0)
                policy.act(observation)
                group["samples"] += 1
                group["changed"] += (
                    policy.current["changed"] + policy.current.get("neighbor_changes", 0) - before
                )
        report[name] = groups
        print(name, groups, flush=True)
        policy.episodes.clear()
    return {
        "reference_laps": len(references),
        "variants": report,
        "leave_one_episode_out_envelope": envelope_holdout(replay),
        "warning": "Action disagreement on logged states is not a lap-time prediction.",
    }


def benchmark(run: Any, policy: Sub37Policy) -> None:
    enable_trial_progress(run, policy)
    enable_clock_diagnostics(run)
    try:
        metrics = dict(run.evaluator.evaluate(policy))
    finally:
        write_json(run.run_dir / "policy-traces.json", policy.episodes)
    artifact = _load_evaluation_artifact(run.run_dir)
    trials = _artifact_trials(artifact)
    write_markdown(run.run_dir, trials)
    _print_benchmark_report(trials, metrics)
    expected = run.spec.evaluation.trials_per_map * len(run.spec.evaluation.maps)
    if len(trials) != expected:
        raise RuntimeError("incomplete benchmark; all configured trials are required")
    _apply_benchmark_gate(trials, metrics, run.spec.evaluation)


def enable_trial_progress(run: Any, policy: Sub37Policy) -> None:
    evaluate_episode = run.evaluator._evaluate_episode

    def logged_episode(request: Any) -> Any:
        result = evaluate_episode(request)
        policy.current["trial_index"] = result.trial_index
        policy.current["finished"] = result.finished
        policy.current["finish_time_s"] = result.finish_time_s
        event = {
            "trial": result.trial_index,
            "finished": result.finished,
            "time_s": result.finish_time_s,
            "telemetry_error": result.telemetry_error,
            "controller_error": result.controller_error,
        }
        with (run.run_dir / "trial-progress.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event) + "\n")
        write_json(run.run_dir / "policy-traces.json", policy.episodes)
        print(json.dumps(event), flush=True)
        return result

    run.evaluator._evaluate_episode = logged_episode


def enable_clock_diagnostics(run: Any) -> None:
    take_step = run.evaluator._take_step

    def measured_step(loop: Any) -> Any:
        previous = float(loop.observation[3])
        result = take_step(loop)
        if result.info.get("step_race_time_ms", 0.0) <= 0.0:
            event = {
                "previous_race_time_ms": previous,
                "info": result.info,
                "terminated": result.terminated,
                "truncated": result.truncated,
            }
            with (run.run_dir / "clock-anomalies.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, default=str) + "\n")
        return result

    run.evaluator._take_step = measured_step


def write_markdown(directory: Path, trials: list[dict[str, Any]]) -> None:
    lines = [
        "# Sub37 experimental benchmark",
        "",
        "All attempts, in recorded order.",
        "",
        "| Trial | Finished | Time (s) |",
        "| --- | --- | --- |",
    ]
    for trial in trials:
        lines.append(f"| {trial['trial_index']} | {trial['finished']} | {trial['finish_time_s']} |")
    times = [float(trial["finish_time_s"]) for trial in trials if trial["finished"]]
    if len(times) == len(trials) and times:
        lines.extend(["", f"Raw mean: {np.mean(times):.3f} s; best: {min(times):.3f} s."])
    else:
        lines.extend(
            ["", "FAIL: at least one unfinished attempt; no all-attempt finish-time mean."]
        )
    lines.extend(
        [
            "",
            "Runtime health and acceptance: see evaluation.json and console gate.",
            "Exact intervention and checkpoint hash: experiment.json.",
        ]
    )
    (directory / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parser().parse_args()
    torch.set_num_threads(2)
    args.checkpoint = args.checkpoint.resolve(strict=True)
    args.config = args.config.resolve(strict=True)
    run = resolve_run(experiment_spec(args), base_dir=args.config.parent)
    try:
        write_json(run.run_dir / "resolved-spec.json", run.spec.model_dump(mode="json"))
        shutil.copyfile(Path(__file__), run.run_dir / "runner-source.py")
        shutil.copyfile(
            Path(__file__).with_name("policy.py"),
            run.run_dir / "policy-source.py",
        )
        _load_checkpoint(run, args.checkpoint)
        checkpoint = run.checkpoint_codec.load(args.checkpoint)
        replay = checkpoint["replay_store"]
        policy_type = NeighborPolicy if "neighbors" in args.variant else Sub37Policy
        policy = policy_type(
            run.learner.policy(), EXPERIMENTS[args.variant], build_envelope(replay)
        )
        if isinstance(policy, NeighborPolicy):
            policy.configure_references(replay)
            shutil.copyfile(
                Path(__file__).with_name("neighbors.py"),
                run.run_dir / "neighbor-source.py",
            )
        write_json(
            run.run_dir / "experiment.json",
            {
                "experiment": asdict(policy.experiment),
                "config": str(args.config),
                "checkpoint": str(args.checkpoint),
                "sha256": _file_sha256(args.checkpoint),
                "config_sha256": _file_sha256(args.config),
                "runner_code_sha256": _file_sha256(Path(__file__).resolve()),
                "policy_code_sha256": _file_sha256(Path(__file__).with_name("policy.py")),
                "reference_laps": len(reference_episodes(replay)),
                "envelope": policy.envelope.cpu().tolist(),
            },
        )
        print(f"Results: {run.run_dir}", flush=True)
        if args.mode == "offline":
            write_json(run.run_dir / "offline-screen.json", offline_screen(policy, replay))
        else:
            benchmark(run, policy)
    finally:
        run.logger.close()


if __name__ == "__main__":
    main()
