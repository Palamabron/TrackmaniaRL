"""Bounded calibration trajectory to locate drift; fixed controls, no runtime promotion."""

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
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--history", type=Path, required=True)
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
    learner_pin = tree_digest(state["learner"])
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

    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    assert reference["checkpoint_sha256"] == args.expected_sha
    assert reference["split_rows"] == {k: v.tolist() for k, v in groups.items()}
    history = json.loads(args.history.read_text(encoding="utf-8"))
    assert history["checkpoint_sha256"] == args.expected_sha
    reasons = {x["row"]: x["endpoint_log"]["termination"] for x in history["terminal_records"]}
    metrics_positions = dict(positions)
    for reason in sorted(set(reasons.values())):
        metrics_positions["held_" + reason] = np.asarray(
            [i for i in positions["held_terminal"] if reasons[int(rows[i])] == reason]
        )
    started = time.monotonic()

    def check_cap() -> None:
        if time.monotonic() - started > 300:
            raise TimeoutError("300s fixed trajectory compute cap; never extend")

    def evaluate(candidate: Any) -> dict[str, Any]:
        measured: dict[str, list[torch.Tensor]] = {k: [] for k in ("mae", "mse", "clipped")}
        with torch.no_grad():
            for chunk in np.array_split(np.arange(len(rows)), max(1, int(np.ceil(len(rows) / 64)))):
                check_cap()
                current = torch.stack(h.selected(candidate, h.subset(batch, chunk)))
                error = current - targets[chunk]
                clipped = old[:, chunk] + (current - old[:, chunk]).clamp(
                    -options["q_clip_epsilon"], options["q_clip_epsilon"]
                )
                measured["mae"].append(error.abs().mean(0))
                measured["mse"].append(error.square().sum(0))
                measured["clipped"].append(
                    torch.maximum(error.square(), (clipped - targets[chunk]).square()).sum(0)
                )
        all_metrics = {k: torch.cat(v).numpy() for k, v in measured.items()}
        result = {
            group + "_" + metric: float(values[pos].mean())
            for group, pos in metrics_positions.items()
            if len(pos)
            for metric, values in all_metrics.items()
        }
        result["held_terminal_per_episode"] = all_metrics["mae"][
            positions["held_terminal"]
        ].tolist()
        return result

    baseline = evaluate(model)
    assert all(
        abs(baseline[k] - v) < 1e-6
        for k, v in reference["baseline"].items()
        if isinstance(v, (int, float))
    )
    report: dict[str, Any] = {
        "status": "RUNNING",
        "checkpoint_sha256": args.expected_sha,
        "baseline": baseline,
        "split_rows": {k: v.tolist() for k, v in groups.items()},
        "design": {
            "weights": [0, 0.01],
            "seeds": [17, 29],
            "steps_per_copy": 48,
            "trace_steps": [0, 1, 4, 8, 16, 32, 48],
            "cap_seconds": 300,
            "purpose": "Locate onset and objective-vs-MAE drift; no early checkpoint promotion",
            "same_saved_adam_projection_frozen_targets_sampling_as_reference": True,
        },
        "results": [],
        "cpu_threads": 1,
        "priority": "IDLE",
        "runtime_learner_updates": 0,
        "controller_created": False,
    }

    def save() -> None:
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")

    save()
    for weight in (0, 0.01):
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
            cell: dict[str, Any] = {
                "lambda": weight,
                "seed": seed,
                "trace": [{"step": 0, **baseline}],
            }
            report["results"].append(cell)
            for step in range(1, 49):
                check_cap()
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
                if step in (1, 4, 8, 16, 32, 48):
                    cell["trace"].append({"step": step, **evaluate(candidate)})
                    save()
            endpoint = cell["trace"][-1]
            prior = next(
                r for r in reference["results"] if r["lambda"] == weight and r["seed"] == seed
            )
            matched = {k: abs(endpoint[k] - v) for k, v in prior.items() if k.endswith("_mae")}
            assert all(v < 1e-6 for v in matched.values()), matched
            cell["endpoint_reference_max_error"] = max(matched.values())
            cell["first_sampled_initial_guard_failure_step"] = next(
                (
                    t["step"]
                    for t in cell["trace"]
                    if t["held_nonterminal_mae"] > 1.2 * baseline["held_nonterminal_mae"]
                ),
                None,
            )
            cell["final_guard_passed"] = (
                endpoint["held_nonterminal_mae"] <= 1.2 * baseline["held_nonterminal_mae"]
            )
            print(
                json.dumps(
                    {
                        "weight": weight,
                        "seed": seed,
                        "first_sampled_guard_failure": cell[
                            "first_sampled_initial_guard_failure_step"
                        ],
                        "endpoint_match": cell["endpoint_reference_max_error"],
                    }
                ),
                flush=True,
            )
            save()
            del candidate, optimizer
    assert pins == [h.model_digest(item) for item in (model, target)]
    assert learner_pin == tree_digest(state["learner"])
    assert h.sha(args.checkpoint) == args.expected_sha
    report.update(
        status="COMPLETE",
        elapsed_seconds=time.monotonic() - started,
        original_model_target_all_optimizers_unchanged=True,
        total_copy_optimizer_steps=192,
        all_endpoints_match=True,
        limitation=(
            "Frozen targets and reused replay; diagnostic trajectory only, "
            "no driving or early checkpoint promotion."
        ),
    )
    save()


if __name__ == "__main__":
    main()
