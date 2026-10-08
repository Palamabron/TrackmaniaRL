"""CPU, idle, one-thread inference on every saved episode start; zero updates."""

from __future__ import annotations

import argparse
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
from trackmaniarl.models.backbones import HypersphericalLinear


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
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
    obs = helper.decode_tree(replay["observations"], rows)
    with torch.no_grad():
        q1, q2 = model.q1(obs), model.q2(obs)
        logs = model.actor.log_probabilities(obs)
        actor = logs.argmax(1)
        options = state["learner"]["sd_sac_options"]
        alpha = max(
            float(state["learner"]["log_alpha"].exp()), options["entropy_coefficient_min"] or 0
        )
        if options["entropy_coefficient_max"] is not None:
            alpha = min(alpha, options["entropy_coefficient_max"])
        result: dict[str, Any] = {}
        for name, q in (("q1", q1), ("q2", q2), ("minimum", torch.minimum(q1, q2))):
            tops = q.argmax(1)
            values, counts = tops.unique(return_counts=True)
            result[name] = {
                "margin": h.summary((q.max(1).values - q.min(1).values).numpy()),
                "top_gap": h.summary((q.topk(2, dim=1).values.diff(dim=1).abs()).numpy()),
                "top_action_counts": dict(zip(values.tolist(), counts.tolist(), strict=True)),
                "actor_greedy_agreement": float((actor == tops).float().mean()),
                "actor_regret": h.summary(
                    (q.max(1).values - q.gather(1, actor[:, None])[:, 0]).numpy()
                ),
                "action21_regret": h.summary((q.max(1).values - q[:, 21]).numpy()),
                "action21_fraction_actions_below": h.summary(
                    (q < q[:, 21:22]).float().mean(1).numpy()
                ),
                "soft_target_entropy": h.summary(
                    (
                        -(
                            torch.softmax(q / alpha, dim=1) * torch.log_softmax(q / alpha, dim=1)
                        ).sum(1)
                    ).numpy()
                ),
            }
        values, counts = actor.unique(return_counts=True)
        result["actor_action_counts"] = dict(zip(values.tolist(), counts.tolist(), strict=True))
        result["actor_entropy"] = h.summary((-(logs.exp() * logs).sum(1)).numpy())
        result["weight_row_norms"] = {
            name: h.summary(layer.weight.norm(dim=1).numpy())
            for name, layer in model.named_modules()
            if isinstance(layer, HypersphericalLinear)
        }
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
    print("Initial landscape audit saved")


if __name__ == "__main__":
    main()
