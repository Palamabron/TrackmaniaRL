"""Bounded CPU-only critic/Adam copies with frozen targets and projected weights."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["WANDB_MODE"] = "disabled"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np
import psutil
import torch

from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.models.backbones import project_hyperspherical_weights


def tree_digest(value: Any) -> str:
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


@dataclass(frozen=True)
class LossSettings:
    terminal_fraction: float
    terminal_weight: float
    epsilon: float


def calibration_loss(
    values: tuple[torch.Tensor, torch.Tensor, torch.Tensor], settings: LossSettings
) -> torch.Tensor:
    """First half N, second half T; baseline restores empirical class prevalence."""
    current, old, target = values
    count = current.shape[1] // 2
    clipped = old + (current - old).clamp(-settings.epsilon, settings.epsilon)
    errors = (current - target).square()
    clipped_errors = torch.maximum(errors, (clipped - target).square()).sum(0)
    return (
        (1 - settings.terminal_fraction) * clipped_errors[:count].mean()
        + settings.terminal_fraction * clipped_errors[count:].mean()
        + settings.terminal_weight * errors[:, count:].sum(0).mean()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Never overwrite a prior probe")
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    support = importlib.util.spec_from_file_location(
        "probe_support", Path(__file__).with_name("probe_sd_sac_critic.py")
    )
    assert support is not None
    assert support.loader is not None
    h = importlib.util.module_from_spec(support)
    support.loader.exec_module(h)
    if h.sha(args.checkpoint) != args.expected_sha:
        raise ValueError("Checkpoint SHA mismatch")
    state = h.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    if run_fingerprint(spec, Path.cwd()) != state["run_fingerprint"]:
        raise ValueError("Runtime/config fingerprint mismatch")
    if spec.training.n_step != 1:
        raise ValueError("One-step snapshot required")
    factory = spec.components.model_factory
    assert factory is not None
    model, target = [_instantiate(factory).build() for _ in range(2)]
    for item, key in ((model, "model"), (target, "target_model")):
        item.load_state_dict(state["learner"][key], strict=True)
        item.eval().requires_grad_(False)
    pins = [h.model_digest(item) for item in (model, target)]
    adam_pin = tree_digest(state["learner"]["critic_optimizer"])
    options = state["learner"]["sd_sac_options"]
    alpha = max(float(state["learner"]["log_alpha"].exp()), options["entropy_coefficient_min"] or 0)
    if options["entropy_coefficient_max"] is not None:
        alpha = min(alpha, options["entropy_coefficient_max"])
    replay = state["replay_store"]
    size = int(replay["size"])
    index = np.arange(size)
    following = np.asarray(replay["next_ids"])[:size] - (int(replay["next_index"]) - size)
    bounded = np.clip(following, 0, size - 1)
    terminated = np.asarray(replay["terminated"])[:size]
    truncated = np.asarray(replay["truncated"])[:size]
    linked = (
        (following > index)
        & (following < size)
        & (replay["episode_codes"][:size] == replay["episode_codes"][bounded])
        & (replay["steps"][bounded] == replay["steps"][:size] + 1)
    )
    eligible = ~truncated & (terminated | linked)
    fit_rows, held_rows = h.split_episodes(replay["episode_codes"][:size], seed=17421)
    fit_mask, held_mask = np.isin(index, fit_rows), np.isin(index, held_rows)
    rng = np.random.default_rng(17422)
    groups = {}
    for name, mask in (("fit", fit_mask), ("held", held_mask)):
        groups[name + "_terminal"] = np.flatnonzero(mask & eligible & terminated)
        pool = np.flatnonzero(mask & eligible & ~terminated)
        groups[name + "_nonterminal"] = rng.choice(pool, min(1024, len(pool)), False)
    if any(len(rows) < 5 for rows in groups.values()):
        raise ValueError("Insufficient episode-held classes")
    p_terminal = float(terminated[fit_mask & eligible].mean())
    rows = np.concatenate(list(groups.values()))
    batch = h.materialize(replay, rows, spec.training.gamma)
    positions = {}
    offset = 0
    for name, selected_rows in groups.items():
        positions[name] = np.arange(offset, offset + len(selected_rows))
        offset += len(selected_rows)
    frozen_targets, old_values = [], []
    with torch.no_grad():
        for chunk in np.array_split(np.arange(len(rows)), max(1, int(np.ceil(len(rows) / 64)))):
            part = h.subset(batch, chunk)
            logs = model.actor.log_probabilities(part.next_observations)
            q = (target.q1(part.next_observations) + target.q2(part.next_observations)) / 2
            continuation = (logs.exp() * (q - alpha * logs)).sum(1)
            frozen_targets.append(part.rewards + part.discounts * continuation)
            old_values.append(torch.stack(h.selected(target, part)))
    targets, old = torch.cat(frozen_targets), torch.cat(old_values, dim=1)

    def evaluate(candidate: Any) -> dict[str, Any]:
        errors = []
        with torch.no_grad():
            for chunk in np.array_split(np.arange(len(rows)), max(1, int(np.ceil(len(rows) / 64)))):
                current = torch.stack(h.selected(candidate, h.subset(batch, chunk)))
                errors.append((current - targets[chunk]).abs().mean(0))
        all_errors = torch.cat(errors).numpy()
        return {
            **{name + "_mae": float(all_errors[pos].mean()) for name, pos in positions.items()},
            "held_terminal_per_episode": all_errors[positions["held_terminal"]].tolist(),
        }

    baseline = evaluate(model)
    limit = 1.2 * baseline["held_nonterminal_mae"]
    report: dict[str, Any] = {
        "status": "RUNNING",
        "checkpoint_sha256": args.expected_sha,
        "baseline": baseline,
        "held_nonterminal_mae_limit": limit,
        "split_rows": {name: value.tolist() for name, value in groups.items()},
        "held_terminal_episode_codes": replay["episode_codes"][groups["held_terminal"]].tolist(),
        "design": {
            "steps_per_copy": 48,
            "seeds": [17, 29],
            "terminal_weights": [0, 0.01, 0.1, 1],
            "empirical_fit_terminal_fraction": p_terminal,
            "objective": "empirical-frequency clipped Bellman loss + lambda*mean_terminal_MSE",
            "class_sampling": "128 nonterminals +128 terminals, with replacement",
            "targets": "Frozen saved actor, target critics, alpha and bootstrap discounts",
            "projection": "q1/q2 after each saved-Adam step; no Polyak updates",
            "holdout": "Whole episodes excluded from fitting; replay already used in training",
            "cap_seconds": 600,
        },
        "results": [],
        "cpu_threads": 1,
        "priority": "IDLE",
        "runtime_learner_updates": 0,
        "controller_created": False,
    }
    started = time.monotonic()
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    for weight in (0, 0.01, 0.1, 1):
        for seed in (17, 29):
            candidate = SimpleNamespace(q1=copy.deepcopy(model.q1), q2=copy.deepcopy(model.q2))
            for critic in (candidate.q1, candidate.q2):
                critic.requires_grad_(True)
            optimizer = torch.optim.Adam(
                list(candidate.q1.parameters()) + list(candidate.q2.parameters()),
                lr=options["learning_rate"],
            )
            optimizer.load_state_dict(copy.deepcopy(state["learner"]["critic_optimizer"]))
            sample = np.random.default_rng(seed)
            for _ in range(48):
                if time.monotonic() - started > 600:
                    raise TimeoutError("600s disposable probe cap")
                selected = np.r_[
                    sample.choice(positions["fit_nonterminal"], 128),
                    sample.choice(positions["fit_terminal"], 128),
                ]
                current = torch.stack(h.selected(candidate, h.subset(batch, selected)))
                loss = calibration_loss(
                    (current, old[:, selected], targets[selected]),
                    LossSettings(p_terminal, weight, options["q_clip_epsilon"]),
                )
                assert torch.isfinite(loss)
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
                project_hyperspherical_weights(candidate.q1)
                project_hyperspherical_weights(candidate.q2)
            measured = evaluate(candidate)
            report["results"].append(
                {
                    "lambda": weight,
                    "seed": seed,
                    "copy_steps": 48,
                    **measured,
                    "drift_guard_passed": measured["held_nonterminal_mae"] <= limit,
                }
            )
            args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"Completed critic copy lambda={weight} seed={seed}", flush=True)
            del candidate, optimizer
    # Paired held-episode bootstrap; family correction over three nonzero candidates.
    comparison = []
    for weight in (0.01, 0.1, 1):
        selected = [r for r in report["results"] if r["lambda"] == weight]
        reference = [r for r in report["results"] if r["lambda"] == 0]
        reduction = np.mean(
            [
                np.asarray(r["held_terminal_per_episode"])
                - np.asarray(c["held_terminal_per_episode"])
                for r, c in zip(reference, selected, strict=True)
            ],
            axis=0,
        )
        bootstrap = np.random.default_rng(17423).choice(reduction, (20000, len(reduction))).mean(1)
        low, high = np.quantile(bootstrap, [0.05 / 6, 1 - 0.05 / 6])
        comparison.append(
            {
                "lambda": weight,
                "mean_held_terminal_reduction_vs_zero": float(reduction.mean()),
                "family_adjusted_interval": [float(low), float(high)],
                "both_seed_drift_guards_pass": all(r["drift_guard_passed"] for r in selected),
                "positive_lower_bound": bool(low > 0),
                "baseline_terminal_improved_both_seeds": all(
                    r["held_terminal_mae"] < baseline["held_terminal_mae"] for r in selected
                ),
            }
        )
    assert pins == [h.model_digest(item) for item in (model, target)]
    assert adam_pin == tree_digest(state["learner"]["critic_optimizer"])
    assert h.sha(args.checkpoint) == args.expected_sha
    report.update(
        status="COMPLETE",
        comparison=comparison,
        elapsed_seconds=time.monotonic() - started,
        saved_checkpoint_models_adam_unchanged=True,
        total_copy_optimizer_steps=384,
        limitation="Frozen targets and reused replay do not establish driving quality.",
    )
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()
