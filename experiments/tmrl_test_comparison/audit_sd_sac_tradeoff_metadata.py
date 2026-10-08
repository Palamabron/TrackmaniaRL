"""Audit replay metadata behind paired greedy-regret deterioration; zero model updates."""

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
from trackmaniarl.core.spec import RunSpec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output", "ordinary", "combination"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    spec = importlib.util.spec_from_file_location(
        "support", Path(__file__).with_name("probe_sd_sac_actor_plasticity.py")
    )
    assert spec is not None
    assert spec.loader is not None
    support = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(support)
    helper = support.load_helper()
    assert helper.sha(args.checkpoint) == args.expected_sha
    state = helper.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    assert run_fingerprint(RunSpec.from_yaml(args.config), Path.cwd()) == state["run_fingerprint"]
    model_pin = helper.tree_digest(state["learner"]["model"])
    adam_pin = helper.tree_digest(state["learner"]["actor_optimizer"])
    ordinary = json.loads(args.ordinary.read_text())
    combo = json.loads(args.combination.read_text())
    assert ordinary["checkpoint_sha256"] == combo["checkpoint_sha256"] == args.expected_sha
    assert ordinary["rows"]["held"] == combo["rows"]["held"]
    rows = np.asarray(combo["rows"]["held"])
    replay = state["replay_store"]
    obs = helper.decode_tree(replay["observations"], rows)
    physics = obs["physics"].numpy()
    # Frozen graph_iqn_v2._motion_scalars: speed/100, forward_speed/100, lateral, progress.
    assert physics.shape == (len(rows), 60)
    metadata = {
        "step": np.asarray(replay["steps"])[rows],
        "speed_mps": physics[:, 0] * 100,
        "forward_speed_mps": physics[:, 1] * 100,
        "progress_fraction": physics[:, 3],
        "terminated": np.asarray(replay["terminated"])[rows],
        "truncated": np.asarray(replay["truncated"])[rows],
    }

    def summary(values: Any) -> dict[str, Any]:
        values = np.asarray(values, dtype=np.float64)
        assert np.isfinite(values).all()
        if not len(values):
            return {"count": 0}
        return {
            "count": len(values),
            "min": float(values.min()),
            "median": float(np.median(values)),
            "mean": float(values.mean()),
            "max": float(values.max()),
        }

    results = []
    for result in combo["results"]:
        seed = result["seed"]
        reference = next(
            x
            for x in ordinary["results"]
            if x["seed"] == seed and x["objective"] == "forward" and x["lr"] == 0.0009
        )
        candidate = result["metrics"]["held"]
        base = reference["metrics"]["held"]
        deltas = np.asarray(candidate["greedy_regret_per_row"]) - np.asarray(
            base["greedy_regret_per_row"]
        )
        grouped = {}
        for name, mask in (
            ("worsened", deltas > 1e-8),
            ("improved", deltas < -1e-8),
            ("unchanged", abs(deltas) <= 1e-8),
        ):
            indices = np.flatnonzero(mask)
            transitions: dict[str, int] = {}
            for i in indices:
                key = str(base["greedy_actions"][i]) + "->" + str(candidate["greedy_actions"][i])
                transitions[key] = transitions.get(key, 0) + 1
            grouped[name] = {
                "metadata": {key: summary(value[mask]) for key, value in metadata.items()},
                "action_transitions": transitions,
                "distinct_episodes": len(
                    np.unique(np.asarray(replay["episode_codes"])[rows[mask]])
                ),
            }
        order = np.argsort(-deltas)[:20]
        results.append(
            {
                "seed": seed,
                "groups": grouped,
                "worst20": [
                    {
                        "row": int(rows[i]),
                        "regret_increase": float(deltas[i]),
                        **{key: float(value[i]) for key, value in metadata.items()},
                        "ordinary_action": base["greedy_actions"][i],
                        "combination_action": candidate["greedy_actions"][i],
                    }
                    for i in order
                ],
            }
        )
    assert helper.sha(args.checkpoint) == args.expected_sha
    assert helper.tree_digest(state["learner"]["model"]) == model_pin
    assert helper.tree_digest(state["learner"]["actor_optimizer"]) == adam_pin
    report = {
        "status": "COMPLETE",
        "checkpoint_sha256": args.expected_sha,
        "original_model_adam_checkpoint_unchanged": True,
        "optimizer_steps": 0,
        "controller_created": False,
        "runtime_learner_updates": 0,
        "cpu_threads": 1,
        "priority": "IDLE",
        "results": results,
        "limitation": "Replay metadata and frozen-Q regret; no driving or true action-value claim.",
    }
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False))
    print(json.dumps({"status": "COMPLETE", "results": results}))


if __name__ == "__main__":
    main()
