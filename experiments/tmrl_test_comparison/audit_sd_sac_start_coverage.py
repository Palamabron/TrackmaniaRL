"""Audit saved start-state coverage, observation identity and categorical margins; no updates."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["WANDB_MODE"] = "disabled"

import numpy as np
import psutil
import torch

from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--probe", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    support = importlib.util.spec_from_file_location(
        "audit_support", Path(__file__).with_name("audit_sd_sac_critic.py")
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
    factory = spec.components.model_factory
    assert factory is not None
    model = _instantiate(factory).build()
    model.load_state_dict(state["learner"]["model"], strict=True)
    model.eval().requires_grad_(False)
    before = h.model_digest(model)
    replay = state["replay_store"]
    rows = np.flatnonzero(np.asarray(replay["steps"])[: int(replay["size"])] == 0)
    if not len(rows):
        raise ValueError("No saved initial observations")
    # Use the same replay decoder as the critic audit, including scalar tensors.
    decoder = importlib.util.spec_from_file_location(
        "probe_support", Path(__file__).with_name("probe_sd_sac_joint_calibration.py")
    )
    assert decoder is not None
    assert decoder.loader is not None
    helper = importlib.util.module_from_spec(decoder)
    decoder.loader.exec_module(helper)
    prior = json.loads(args.probe.read_text())
    assert prior["checkpoint_sha256"] == args.expected_sha
    options = state["learner"]["sd_sac_options"]
    alpha = max(float(state["learner"]["log_alpha"].exp()), options["entropy_coefficient_min"] or 0)
    if options["entropy_coefficient_max"] is not None:
        alpha = min(alpha, options["entropy_coefficient_max"])

    def leaves(tree: Any, prefix: str = "") -> dict[str, torch.Tensor]:
        if isinstance(tree, dict):
            return {
                p: v
                for key in sorted(tree)
                for p, v in leaves(tree[key], prefix + "/" + str(key)).items()
            }
        if isinstance(tree, (tuple, list)):
            return {
                p: v
                for key, node in enumerate(tree)
                for p, v in leaves(node, prefix + "/" + str(key)).items()
            }
        return {prefix: tree}

    def hashes(flat: dict[str, torch.Tensor]) -> list[str]:
        result = []
        for i in range(len(next(iter(flat.values())))):
            digest = hashlib.sha256()
            for path, tensor in flat.items():
                digest.update(path.encode())
                digest.update(str(tensor.shape[1:]).encode())
                digest.update(str(tensor.dtype).encode())
                digest.update(tensor[i].contiguous().numpy().tobytes())
            result.append(digest.hexdigest())
        return result

    starts = helper.decode_tree(replay["observations"], rows)
    start_flat = leaves(starts)
    start_hashes = set(hashes(start_flat))
    coverage = {}
    for name in ("fit", "held"):
        selected = np.asarray(prior["rows"][name])
        flat = leaves(helper.decode_tree(replay["observations"], selected))
        selected_steps = np.asarray(replay["steps"])[selected]
        exact = np.asarray([value in start_hashes for value in hashes(flat)])
        coverage[name] = {
            "rows": len(selected),
            "episode_first_rows": int((selected_steps == 0).sum()),
            "rows_with_start_identical_observation": int(exact.sum()),
            "nonstart_rows_aliasing_a_start": int((exact & (selected_steps != 0)).sum()),
            "steps": h.summary(selected_steps),
            "nearest_to_first_start_by_leaf": {
                path: float(
                    (
                        tensor.double().reshape(len(selected), -1)
                        - start_flat[path][0].double().flatten()
                    )
                    .square()
                    .mean(1)
                    .sqrt()
                    .min()
                )
                for path, tensor in flat.items()
            },
        }
    with torch.no_grad():
        q = 0.5 * model.q1(starts) + 0.5 * model.q2(starts)
        logs = model.actor.log_probabilities(starts)
        actor_probs, soft_probs = logs.exp(), torch.softmax(q / alpha, 1)
        result: dict[str, Any] = {
            "coverage": coverage,
            "distinct_start_observations": len(start_hashes),
            "start_leaf_shapes": {path: list(tensor.shape) for path, tensor in start_flat.items()},
            "start_leaf_max_abs_difference_from_first": {
                path: float((tensor.double() - tensor[0].double()).abs().max())
                for path, tensor in start_flat.items()
            },
        }
        for name, probs in (("actor", actor_probs), ("soft_mean_q_target", soft_probs)):
            top = probs.topk(2, dim=1)
            actions, counts = top.indices[:, 0].unique(return_counts=True)
            result[name] = {
                "top_action_counts": dict(zip(actions.tolist(), counts.tolist(), strict=True)),
                "top_probability": h.summary(top.values[:, 0].numpy()),
                "top_two_probability_gap": h.summary((top.values[:, 0] - top.values[:, 1]).numpy()),
                "probability_action35": h.summary(probs[:, 35].numpy()),
                "probability_action56": h.summary(probs[:, 56].numpy()),
                "entropy": h.summary((-(probs * probs.clamp_min(1e-30).log()).sum(1)).numpy()),
            }
        result["mean_q_top_two_gap"] = h.summary(
            (q.topk(2, dim=1).values[:, 0] - q.topk(2, dim=1).values[:, 1]).numpy()
        )
    assert h.sha(args.checkpoint) == args.expected_sha
    assert h.model_digest(model) == before
    result.update(
        checkpoint_sha256=args.expected_sha,
        initial_observations=len(rows),
        transition_rows=rows.tolist(),
        alpha=alpha,
        optimizer_steps=0,
        cpu_threads=1,
        priority="IDLE",
        controller_created=False,
        limitation="Replay inference and critic agreement do not establish "
        "correct action values or driving quality.",
    )
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
