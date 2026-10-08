"""Inspect causal terminal history metadata and observation coverage; zero updates."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import time
from collections import Counter
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
from trackmaniarl.experiments.graph_iqn_v3 import CONTEXT_V3_LAYOUT
from trackmaniarl.experiments.graph_iqn_v5 import RECOVERY_V5_LAYOUT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--events", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    support = importlib.util.spec_from_file_location(
        "history_support", Path(__file__).with_name("probe_sd_sac_actor_plasticity.py")
    )
    assert support is not None
    assert support.loader is not None
    h = importlib.util.module_from_spec(support)
    support.loader.exec_module(h)
    helper = h.load_helper()
    assert helper.sha(args.checkpoint) == args.expected_sha
    state = helper.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    assert run_fingerprint(spec, Path.cwd()) == state["run_fingerprint"]
    pin = helper.tree_digest(state["learner"])
    factory = spec.components.model_factory
    assert factory is not None
    model = _instantiate(factory).build()
    model.load_state_dict(state["learner"]["model"], strict=True)
    model.eval().requires_grad_(False)
    model_pin = helper.model_digest(model)
    replay = state["replay_store"]
    size = int(replay["size"])
    first = int(replay["next_index"]) - size
    rows = np.flatnonzero(np.asarray(replay["terminated"][:size], dtype=bool))
    episodes = np.asarray(replay["episode_codes"][:size])
    steps = np.asarray(replay["steps"][:size])
    lookup = {(int(episodes[r]), int(steps[r])): r for r in range(size)}
    assert len(lookup) == size
    obs = helper.decode_tree(replay["observations"], rows)
    actions = helper.decode_tree(replay["actions"], rows).long().flatten()
    begun = time.monotonic()
    with torch.no_grad():
        q_values = {
            name: torch.cat(
                [
                    getattr(model, name)(h.indexed(obs, slice(i, i + 128)))
                    for i in range(0, len(rows), 128)
                ]
            )
            .gather(1, actions[:, None])[:, 0]
            .tolist()
            for name in ("q1", "q2")
        }
    fields = (
        "termination_reason",
        "steps_since_progress",
        "window_progress_m",
        "accepted_progress_delta_m",
        "nearest_distance_m",
        "race_time_ms",
        "progress_m",
    )
    events_pin = helper.sha(args.events)
    episode_events = {}
    with args.events.open(encoding="utf-8") as stream:
        for line in stream:
            event = json.loads(line)
            if event.get("event") == "train/episode":
                payload = event["payload"]
                name = payload["episode_id"]
                assert name not in episode_events
                episode_events[name] = payload
    records: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        if time.monotonic() - begun > 180:
            raise TimeoutError("Fixed 180s audit cap")
        previous = lookup.get((int(episodes[row]), int(steps[row]) - 1))
        if previous is not None:
            assert int(replay["next_ids"][previous]) - first == row
            assert not replay["terminated"][previous]
            assert not replay["truncated"][previous]
        before = replay["info"].get(first + previous, {}) if previous is not None else {}
        after = replay["info"].get(first + int(row), {})
        episode_name = replay["episode_names"][int(episodes[row])]
        endpoint = episode_events.get(episode_name, {})
        if endpoint:
            assert int(endpoint["steps"]) == int(steps[row]) + 1
        records.append(
            {
                "episode_name": episode_name,
                "endpoint_log": {
                    k: endpoint.get(k)
                    for k in (
                        "termination",
                        "steps",
                        "progress/steps_since",
                        "progress/window_m",
                        "progress/nearest_distance_m",
                        "progress/accepted_delta_m",
                    )
                },
                "row": int(row),
                "episode": int(episodes[row]),
                "step": int(steps[row]),
                "action": int(actions[i]),
                "reward": float(replay["rewards"][row]),
                "truncated": bool(replay["truncated"][row]),
                "previous_row": previous,
                "causal_before_action_metadata": {k: before.get(k) for k in fields},
                "after_action_metadata": {k: after.get(k) for k in fields},
                "taken_q": {name: values[i] for name, values in q_values.items()},
                "observation_context": dict(
                    zip(CONTEXT_V3_LAYOUT, obs["context"][i].tolist(), strict=True)
                ),
                "observation_recovery": dict(
                    zip(RECOVERY_V5_LAYOUT, obs["recovery"][i].tolist(), strict=True)
                ),
            }
        )
    grouped = {}
    for reason in sorted({str(x["endpoint_log"]["termination"]) for x in records}):
        group = [x for x in records if str(x["endpoint_log"]["termination"]) == reason]
        grouped[reason] = {
            "count": len(group),
            "q_terminal_reward_mae": {
                name: float(np.mean([abs(x["taken_q"][name] - x["reward"]) for x in group]))
                for name in q_values
            },
            "causal_before_metadata_available": {
                k: sum(x["causal_before_action_metadata"][k] is not None for x in group)
                for k in fields
            },
            "endpoint_steps_since_progress_values": dict(
                Counter(str(x["endpoint_log"]["progress/steps_since"]) for x in group)
            ),
            "causal_steps_since_progress_values": dict(
                Counter(
                    str(x["causal_before_action_metadata"]["steps_since_progress"]) for x in group
                )
            ),
        }
    cfg = spec.components.environment.kwargs["config"]
    assert helper.sha(args.events) == events_pin
    assert helper.tree_digest(state["learner"]) == pin
    assert helper.model_digest(model) == model_pin
    assert helper.sha(args.checkpoint) == args.expected_sha
    source_files = [
        "trackmaniarl/distributed/coordinator_ingest.py",
        "trackmaniarl/trackmania/reward_step.py",
        "trackmaniarl/trackmania/environment_step.py",
        "trackmaniarl/experiments/graph_iqn_v2.py",
        "trackmaniarl/experiments/graph_iqn_v3.py",
        "trackmaniarl/experiments/graph_iqn_v5.py",
    ]
    report = {
        "status": "COMPLETE",
        "checkpoint_sha256": args.expected_sha,
        "events_sha256": events_pin,
        "replay_info_keys": sorted({k for info in replay["info"].values() for k in info}),
        "fingerprint": state["run_fingerprint"],
        "original_model_all_optimizers_unchanged": True,
        "optimizer_steps": 0,
        "controller_created": False,
        "cpu_threads": 1,
        "priority": "IDLE",
        "elapsed_seconds": time.monotonic() - begun,
        "config_thresholds": {
            k: cfg[k]
            for k in (
                "no_progress_steps",
                "slow_progress_window_steps",
                "minimum_progress_per_window_m",
                "crash_distance",
                "maximum_race_time_s",
            )
        },
        "frozen_source_sha256": {p: helper.sha(Path(p)) for p in source_files},
        "observation_shapes": {k: list(v.shape[1:]) for k, v in obs.items()},
        "groups": grouped,
        "terminal_records": records,
        "source_findings": [
            "No-progress uses steps since advance; slow-progress uses a reward history window.",
            "V5 omits explicit reward-history counters and absolute race time.",
            "Frame advance and incident memory differ from reward-history counters.",
            "Replay info is post-action; previous consecutive-row info is causal pre-action.",
        ],
        "limitations": [
            "Missing counters do not prove non-identifiability or failure causality.",
            "Post-action metadata must not be used as current-observation training input.",
            "Terminal errors describe these rows, not policy value truth for other states.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"status": "COMPLETE", "groups": grouped}))


if __name__ == "__main__":
    main()
