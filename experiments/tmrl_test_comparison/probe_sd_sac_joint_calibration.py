"""Two-stage CPU-only diagnostic; optimizes only disposable critic/Adam copies.

Run this file with cwd and PYTHONPATH restricted to the checkpoint's frozen
runtime. Supply the prior probe JSON and saved start-observation audit JSON.
The eight lambda/seed pairs receive 48 updates each: 384 total, never a live run.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

if __name__ == "__main__":
    for variable in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        os.environ[variable] = "1"
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["WANDB_MODE"] = "disabled"

import numpy as np
import psutil  # type: ignore[import-untyped]
import torch

if TYPE_CHECKING:
    from experiments.tmrl_test_comparison.audit_sd_sac_critic import (
        decode_tree,
        model_digest,
        read_checkpoint,
        sha,
    )
    from experiments.tmrl_test_comparison.probe_sd_sac_critic import (
        materialize,
        selected,
        subset,
    )
else:
    helper_spec = importlib.util.spec_from_file_location(
        "critic_diagnostic_support", Path(__file__).with_name("probe_sd_sac_critic.py")
    )
    assert helper_spec is not None
    assert helper_spec.loader is not None
    helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)
    decode_tree, materialize, model_digest = (
        helper.decode_tree,
        helper.materialize,
        helper.model_digest,
    )
    read_checkpoint, selected, sha, subset = (
        helper.read_checkpoint,
        helper.selected,
        helper.sha,
        helper.subset,
    )

from trackmaniarl.algorithms.sd_sac_objectives import categorical_statistics
from trackmaniarl.algorithms.stable_discrete_soft_actor_critic import StableDiscreteSoftActorCritic
from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec

CHECKPOINT_SHA = "a243b4f50d210d882860b74e4626ff42b369c3f1c2fd78a25fe81068d05906d7"
LAMBDAS = (0.1, 1.0, 5.0, 10.0)
SEEDS = (17, 29)
STEPS_PER_COPY = 48
DRIFT_LIMIT = 0.145


def stats(value: Any) -> dict[str, float | int]:
    array = np.asarray(value, dtype=np.float64)
    if not array.size or not np.isfinite(array).all():
        raise ValueError("Expected nonempty finite measurements")
    return {
        "count": int(array.size),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "min": float(array.min()),
        "max": float(array.max()),
    }


def landscape(values: np.ndarray, action: int) -> dict[str, Any]:
    """Rank 1 is best; percentile is tie-adjusted, 0=worst and 100=best."""
    if values.ndim != 2 or values.shape[1] < 2 or not np.isfinite(values).all():
        raise ValueError("Expected finite [states, actions] values")
    chosen = values[:, action]
    best = values.argmax(1)
    above = (values > chosen[:, None]).sum(1)
    below = (values < chosen[:, None]).sum(1)
    tied_others = (values == chosen[:, None]).sum(1) - 1
    percentile = 100 * (below + tied_others / 2) / (values.shape[1] - 1)
    actions, counts = np.unique(best, return_counts=True)
    return {
        "margin_max_minus_min": stats(values.max(1) - values.min(1)),
        "top1_action_distribution": dict(zip(map(str, actions), map(int, counts), strict=True)),
        "chosen_action": action,
        "chosen_is_argmax_fraction": float((best == action).mean()),
        "chosen_tied_for_best_fraction": float((above == 0).mean()),
        "chosen_rank_1_best": stats(above + 1),
        "chosen_percentile_100_best": stats(percentile),
        "chosen_q": stats(chosen),
        "best_q": stats(values.max(1)),
        "regret_best_minus_chosen": stats(values.max(1) - chosen),
        "per_state": {
            "top1_action": best.tolist(),
            "chosen_rank": (above + 1).tolist(),
            "chosen_percentile": percentile.tolist(),
            "chosen_q": chosen.tolist(),
            "best_q": values.max(1).tolist(),
            "all_action_q": values.tolist(),
        },
    }


def paired_interval(reductions: np.ndarray, *, seed: int = 17422) -> dict[str, Any]:
    """Episode-cluster paired bootstrap of seed-averaged absolute-error reduction.

    Bonferroni two-sided 98.75% intervals give nominal 95% family coverage for
    four lambda comparisons. Seeds are averaged, not treated as extra episodes.
    """
    if reductions.ndim != 2 or reductions.shape[1] < 2:
        raise ValueError("Expected [sampling seeds, held episodes] reductions")
    by_episode = reductions.mean(0)
    indices = np.random.default_rng(seed).integers(0, len(by_episode), (20000, len(by_episode)))
    means = by_episode[indices].mean(1)
    lower, upper = np.quantile(means, [0.00625, 0.99375])
    return {
        "mean_reduction": float(by_episode.mean()),
        "family_adjusted_interval": [float(lower), float(upper)],
        "positive_lower_bound": bool(lower > 0),
        "episodes": len(by_episode),
        "replicates": 20000,
        "bootstrap_seed": seed,
        "interval_level": 0.9875,
    }


def joint_loss(
    nonterminal_error: torch.Tensor, terminal_error: torch.Tensor, weight: float
) -> torch.Tensor:
    """Separate class means: changing class sample counts cannot change lambda."""
    return nonterminal_error.square().sum(0).mean() + weight * terminal_error.square().sum(0).mean()


def tree_digest(value: Any) -> str:
    """Hash saved Adam scalars and tensors without modifying or serializing them."""
    digest = hashlib.sha256()

    def visit(item: Any) -> None:
        if isinstance(item, torch.Tensor):
            digest.update(str((item.dtype, tuple(item.shape))).encode())
            digest.update(item.detach().cpu().contiguous().numpy().tobytes())
        elif isinstance(item, dict):
            for key in sorted(item, key=repr):
                digest.update(repr(key).encode())
                visit(item[key])
        elif isinstance(item, (list, tuple)):
            for child in item:
                visit(child)
        else:
            digest.update(repr(item).encode())

    visit(value)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("config", "checkpoint", "original-checkpoint", "prior-probe", "starts", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    assert not torch.cuda.is_available()
    started = time.monotonic()
    deadline = started + 900
    files = (args.checkpoint, args.original_checkpoint, args.config, args.prior_probe, args.starts)
    hashes = {str(path): sha(path) for path in files}
    assert hashes[str(args.checkpoint)] == CHECKPOINT_SHA
    assert hashes[str(args.original_checkpoint)] == CHECKPOINT_SHA
    report: dict[str, Any] = {
        "started": datetime.now(UTC).isoformat(),
        "status": "RUNNING",
        "runtime": str(Path.cwd()),
        "runtime_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "input_sha256": hashes,
        "script_sha256": sha(Path(__file__)),
        "helper_sha256": sha(Path(__file__).with_name("probe_sd_sac_critic.py")),
        "stage1_optimizer_steps": 0,
        "copy_optimizer_steps": 0,
        "budget_total_steps": 384,
        "steps_per_copy": STEPS_PER_COPY,
        "cap_seconds": 900,
        "cpu_threads": 1,
        "cpu_interop_threads": 1,
        "priority": "IDLE",
        "controller_created": False,
        "runtime_learner_updates": 0,
        "new_training_runs_created": False,
        "automation": "PAUSED",
        "stage2_grid": [],
    }

    def save() -> None:
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")

    save()
    state = read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    assert spec.training.n_step == 1
    fingerprint = run_fingerprint(spec, Path.cwd())
    assert fingerprint == state["run_fingerprint"]
    report["fingerprint"] = fingerprint
    report["checkpoint_run_id"] = state.get("run_id", spec.run_id)
    factory = spec.components.model_factory
    assert factory is not None
    model, target = _instantiate(factory).build(), _instantiate(factory).build()
    for item, key in ((model, "model"), (target, "target_model")):
        item.load_state_dict(state["learner"][key], strict=True)
        item.eval().requires_grad_(False)
    digests = [model_digest(item) for item in (model, target)]
    adam_digest = tree_digest(state["learner"]["critic_optimizer"])
    replay = state["replay_store"]
    starts = json.loads(args.starts.read_text(encoding="utf-8"))
    start_rows = np.array(starts["transition_ids"])
    assert starts["checkpoint_sha256"] == CHECKPOINT_SHA
    assert len(start_rows) == 138
    assert np.array_equal(np.flatnonzero(replay["steps"] == 0), start_rows)
    print("Stage 1: all discrete actions on 138 saved initial states, zero updates", flush=True)
    with torch.no_grad():
        observations = decode_tree(replay["observations"], start_rows)
        probabilities, _ = categorical_statistics(model.actor, observations)
        q1, q2 = model.q1(observations).numpy(), model.q2(observations).numpy()
    actor_actions = probabilities.argmax(1).numpy()
    names, counts = np.unique(actor_actions, return_counts=True)
    report["stage1"] = {
        "states": 138,
        "action_count": q1.shape[1],
        "transition_ids": start_rows.tolist(),
        "actor_greedy_distribution": dict(zip(map(str, names), map(int, counts), strict=True)),
        "q1": landscape(q1, 21),
        "q2": landscape(q2, 21),
        "sd_sac_average_q": landscape(0.5 * (q1 + q2), 21),
        "interpretation": "Rank/percentile describe learned Q, not true action quality.",
    }
    assert digests == [model_digest(item) for item in (model, target)]
    save()
    prior = json.loads(args.prior_probe.read_text(encoding="utf-8"))
    assert CHECKPOINT_SHA in prior["checkpoint_sha256"].values()
    assert prior["split"]["group_sizes"] == [110, 4096, 27, 1024]
    rows = np.array(prior["split"]["selected_rows"])
    assert len(rows) == 5257
    codes = replay["episode_codes"][rows]
    assert not set(codes[:4206]) & set(codes[4206:])
    assert len(set(codes[4206:4233])) == 27
    batch = materialize(replay, rows, spec.training.gamma)
    options = state["learner"]["sd_sac_options"]
    alpha = float(state["learner"]["log_alpha"].exp())
    if options["entropy_coefficient_min"] is not None:
        alpha = max(alpha, options["entropy_coefficient_min"])
    if options["entropy_coefficient_max"] is not None:
        alpha = min(alpha, options["entropy_coefficient_max"])
    context: Any = SimpleNamespace(
        model=model, target_model=target, target_entropy=options["target_entropy"]
    )
    context._desired_entropy = lambda count: StableDiscreteSoftActorCritic._desired_entropy(
        context, count
    )
    fixed = []
    for offset in range(0, len(rows), 128):
        fixed.append(
            StableDiscreteSoftActorCritic._critic_targets(
                context, subset(batch, slice(offset, offset + 128)), torch.tensor(alpha)
            )
        )
    targets = torch.cat(fixed)
    terminal = batch.source.terminated
    assert torch.equal(targets[terminal], batch.rewards[terminal])
    assert bool(terminal[:110].all() & terminal[4206:4233].all())
    assert not bool(terminal[110:4206].any() | terminal[4233:].any())

    def evaluate(item: Any) -> tuple[dict[str, Any], np.ndarray]:
        chunks = []
        with torch.no_grad():
            for offset in range(0, len(rows), 128):
                chunks.append(
                    torch.stack(selected(item, subset(batch, slice(offset, offset + 128))))
                )
        errors = (torch.cat(chunks, 1) - targets).abs().numpy()
        result: dict[str, Any] = {
            name: float(errors[:, begin:end].mean())
            for name, begin, end in (
                ("fit_terminal_mae", 0, 110),
                ("fit_nonterminal_mae", 110, 4206),
                ("held_terminal_mae", 4206, 4233),
                ("held_nonterminal_mae", 4233, 5257),
            )
        }
        return result, errors[:, 4206:4233].mean(0)

    baseline, base_errors = evaluate(model)
    report["stage2_baseline"] = baseline
    report["stage2_design"] = {
        "split": prior["split"],
        "alpha": alpha,
        "objective": "mean_N(sum_critics((Q-y_frozen)^2)) + lambda*mean_T(sum_critics((Q-r)^2))",
        "clipping": False,
        "sampling": "128 nonterminals and 128 terminals, with replacement per step",
        "normalization": "Separate class means; no empirical-frequency importance correction",
        "target_critics_actor_alpha": "Frozen; no target updates or actor/alpha optimization",
        "optimizer": "Deep-copied saved critic Adam state; same saved learning rate",
        "mode": "eval, gradients enabled only on copied q1/q2",
        "held_nonterminal_mae_limit": DRIFT_LIMIT,
        "guard": "Require <=0.145 AND <=1.2*measured baseline in both sampling seeds",
    }
    save()
    for weight in LAMBDAS:
        for seed in SEEDS:
            print(f"Stage 2: lambda={weight}, seed={seed}, 48 disposable steps", flush=True)
            candidate = copy.deepcopy(model)
            candidate.q1.requires_grad_(True)
            candidate.q2.requires_grad_(True)
            optimizer = torch.optim.Adam(
                list(candidate.q1.parameters()) + list(candidate.q2.parameters()),
                lr=options["learning_rate"],
            )
            optimizer.load_state_dict(copy.deepcopy(state["learner"]["critic_optimizer"]))
            random = np.random.default_rng(seed)
            for _ in range(STEPS_PER_COPY):
                if time.monotonic() >= deadline:
                    raise TimeoutError("Offline probe hit its fixed 900s cap")
                indices = np.r_[random.integers(110, 4206, 128), random.integers(0, 110, 128)]
                current = torch.stack(selected(candidate, subset(batch, indices)))
                error = current - targets[indices]
                loss = joint_loss(error[:, :128], error[:, 128:], weight)
                assert bool(torch.isfinite(loss))
                optimizer.zero_grad(set_to_none=True)
                loss.backward()  # type: ignore[no-untyped-call]
                optimizer.step()
                report["copy_optimizer_steps"] += 1
            metrics, errors = evaluate(candidate)
            metrics.update(
                {
                    "lambda": weight,
                    "seed": seed,
                    "steps": STEPS_PER_COPY,
                    "held_terminal_abs_error_per_episode": errors.tolist(),
                    "held_episode_codes": codes[4206:4233].tolist(),
                    "nonterminal_guard_passed": metrics["held_nonterminal_mae"]
                    <= min(DRIFT_LIMIT, 1.2 * baseline["held_nonterminal_mae"]),
                    "held_nonterminal_relative_increase": metrics["held_nonterminal_mae"]
                    / baseline["held_nonterminal_mae"]
                    - 1,
                    "actor_unchanged": model_digest(candidate.actor) == model_digest(model.actor),
                }
            )
            assert metrics["actor_unchanged"]
            report["stage2_grid"].append(metrics)
            save()
            del optimizer, candidate
    comparison = []
    for weight in LAMBDAS:
        pair = [row for row in report["stage2_grid"] if row["lambda"] == weight]
        reductions = np.array(
            [base_errors - np.array(row["held_terminal_abs_error_per_episode"]) for row in pair]
        )
        interval = paired_interval(reductions)
        guard = all(row["nonterminal_guard_passed"] for row in pair)
        comparison.append(
            {
                "lambda": weight,
                "paired_terminal_reduction": interval,
                "both_seeds_guard_passed": guard,
                "diagnostically_viable": guard and interval["positive_lower_bound"],
            }
        )
    report["lambda_decisions"] = comparison
    assert report["copy_optimizer_steps"] == 384
    assert digests == [model_digest(item) for item in (model, target)]
    assert adam_digest == tree_digest(state["learner"]["critic_optimizer"])
    assert hashes == {path: sha(Path(path)) for path in hashes}
    report["immutable_inputs_models_and_saved_adam_unchanged"] = True
    report["limitations"] = [
        "Held episodes were seen during original training; held out only from these copy updates.",
        "Only 27 held terminal episodes/two sampling seeds; no independent training-seed evidence.",
        "Approximate bootstrap intervals, conditional on this checkpoint/split/short budget.",
        "Nonterminal targets are frozen-critic self-consistency, not independent Q truth.",
        "Unclipped class-normalized joint regression differs from production clipped SD-SAC.",
        "No moving target updates, driving test, saved candidate weights, new run or resume.",
    ]
    report["status"] = "COMPLETE"
    report["finished"] = datetime.now(UTC).isoformat()
    report["elapsed_seconds"] = time.monotonic() - started
    save()
    print("COMPLETE: 384 disposable steps; immutable inputs/base models/Adam unchanged", flush=True)


if __name__ == "__main__":
    main()
