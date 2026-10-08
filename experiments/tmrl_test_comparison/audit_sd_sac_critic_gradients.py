"""Zero-update critic gradient alignment by terminal reason on fixed episode splits."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import time
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
from trackmaniarl.models.backbones import HypersphericalLinear


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--calibration", type=Path, required=True)
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
    reference = json.loads(args.calibration.read_text())
    assert reference["checkpoint_sha256"] == args.expected_sha
    assert {k: v.tolist() for k, v in groups.items()} == reference["split_rows"]
    history = json.loads(args.history.read_text())
    assert history["checkpoint_sha256"] == args.expected_sha
    reasons = {}
    for record in history["terminal_records"]:
        row = record["row"]
        assert terminated[row]
        assert int(replay["steps"][row]) == record["step"]
        assert int(replay["episode_codes"][row]) == record["episode"]
        reasons[row] = record["endpoint_log"]["termination"]
    assert set(reasons) == set(np.flatnonzero(terminated))
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

    candidate = SimpleNamespace(q1=copy.deepcopy(model.q1), q2=copy.deepcopy(model.q2))
    named: list[tuple[str, torch.Tensor]] = []
    spherical: set[int] = set()
    for name in ("q1", "q2"):
        critic = getattr(candidate, name).requires_grad_(True)
        named.extend((name + "." + k, p) for k, p in critic.named_parameters())
        spherical.update(
            id(m.weight) for m in critic.modules() if isinstance(m, HypersphericalLinear)
        )
    copy_pins = [h.model_digest(candidate.q1), h.model_digest(candidate.q2)]
    for split in ("fit", "held"):
        pos = positions[split + "_terminal"]
        for reason in sorted(set(reasons.values())):
            positions[split + "_" + reason] = np.asarray(
                [i for i in pos if reasons[int(rows[i])] == reason]
            )
    begun = time.monotonic()
    gradients = {}
    losses: dict[str, Any] = {}
    for name, pos in positions.items():
        for objective in ("clipped", "mse"):
            key = name + "/" + objective
            if not len(pos):
                losses[key] = {"count": 0, "skipped": True}
                continue
            accum = [torch.zeros_like(p) for _, p in named]
            value = 0.0
            for offset in range(0, len(pos), 64):
                if time.monotonic() - begun > 180:
                    raise TimeoutError("180s fixed gradient cap")
                chunk = pos[offset : offset + 64]
                current = torch.stack(h.selected(candidate, h.subset(batch, chunk)))
                error = (current - targets[chunk]).square()
                if objective == "clipped":
                    clipped = old[:, chunk] + (current - old[:, chunk]).clamp(
                        -options["q_clip_epsilon"], options["q_clip_epsilon"]
                    )
                    error = torch.maximum(error, (clipped - targets[chunk]).square())
                loss = error.sum(0).mean()
                assert torch.isfinite(loss)
                gs = torch.autograd.grad(loss, [p for _, p in named])
                weight = len(chunk) / len(pos)
                value += float(loss.detach()) * weight
                for i, g in enumerate(gs):
                    accum[i] += g.detach() * weight
            gradients[key] = accum
            losses[key] = {"count": len(pos), "loss": value}

    def tangent(gs: list[torch.Tensor]) -> list[torch.Tensor]:
        result = []
        for g, (_, p) in zip(gs, named, strict=True):
            if id(p) in spherical:
                unit = torch.nn.functional.normalize(p.detach(), dim=1)
                g = g - (g * unit).sum(1, keepdim=True) * unit
                assert float((g * unit).sum(1).abs().max()) < 1e-4
            result.append(g)
        return result

    def compare(a: list[torch.Tensor], b: list[torch.Tensor]) -> dict[str, float]:
        x, y = [torch.cat([v.double().flatten() for v in gs]) for gs in (a, b)]
        dot = float(x.dot(y))
        return {
            "left_norm": float(x.norm()),
            "right_norm": float(y.norm()),
            "dot": dot,
            "cosine": dot / max(float(x.norm() * y.norm()), 1e-30),
            "right_loss_derivative_under_left_descent": -dot,
        }

    comparisons: dict[str, Any] = {}
    pairs: list[tuple[str, str]] = []
    for key in gradients:
        if key.startswith("fit_"):
            pairs.extend(
                (key, reference)
                for reference in ("fit_nonterminal/clipped", "held_nonterminal/clipped")
            )
            pairs.append((key, key.replace("fit_", "held_", 1)))
    for left, right in pairs:
        if right not in gradients:
            continue
        a, b = gradients[left], gradients[right]
        at, bt = tangent(a), tangent(b)
        comparisons[left + " vs " + right] = {
            "raw": compare(a, b),
            "tangent": compare(at, bt),
            "per_parameter": {
                name: {"raw": compare([a[i]], [b[i]]), "tangent": compare([at[i]], [bt[i]])}
                for i, (name, _) in enumerate(named)
            },
        }
    assert pins == [h.model_digest(item) for item in (model, target)]
    assert copy_pins == [h.model_digest(candidate.q1), h.model_digest(candidate.q2)]
    assert learner_pin == tree_digest(state["learner"])
    assert h.sha(args.checkpoint) == args.expected_sha
    report = {
        "status": "COMPLETE",
        "checkpoint_sha256": args.expected_sha,
        "original_model_target_all_optimizers_unchanged": True,
        "optimizer_steps": 0,
        "controller_created": False,
        "runtime_learner_updates": 0,
        "cpu_threads": 1,
        "priority": "IDLE",
        "cap_seconds": 180,
        "elapsed_seconds": time.monotonic() - begun,
        "alpha": alpha,
        "matched_calibration_split": True,
        "positions_as_replay_rows": {k: rows[v].tolist() for k, v in positions.items()},
        "losses": losses,
        "comparisons": comparisons,
        "input_sha256": {"calibration": h.sha(args.calibration), "history": h.sha(args.history)},
        "limitation": (
            "Local raw/tangent gradients with frozen targets, not Adam steps, finite-step drift, "
            "critic truth or driving evidence. Endpoint reasons label groups only, "
            "never model inputs."
        ),
    }
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False))
    print(
        json.dumps(
            {
                "status": "COMPLETE",
                "elapsed_seconds": report["elapsed_seconds"],
                "alignment": {
                    k: v["tangent"]["cosine"]
                    for k, v in comparisons.items()
                    if "fit_nonterminal" not in k.split(" vs ")[0]
                },
            }
        )
    )


if __name__ == "__main__":
    main()
