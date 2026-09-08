"""Recompute sampled decisions from their exact observations and original checkpoint."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch

from experiments.sub37.audit_activation_sources import digest
from experiments.sub37.neighbors import NeighborPolicy
from experiments.sub37.policy import EXPERIMENTS, build_envelope
from experiments.sub37.runner import experiment_spec
from trackmaniarl.commands.evaluation import _load_checkpoint
from trackmaniarl.core.runtime import resolve_run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument(
        "--enrich", action="store_true", help="Verify every decision and save internal tensors"
    )
    parser.add_argument("--full-path", action="store_true", help="Include Conv1D, head and fusion")
    args = parser.parse_args()
    args.enrich = args.enrich or args.full_path
    os.environ.setdefault("WANDB_MODE", "disabled")
    manifest = json.loads((args.capture / "manifest.json").read_text())
    trials = [json.loads(line) for line in (args.capture / "trials.jsonl").read_text().splitlines()]
    best = min((t for t in trials if t["finished"]), key=lambda t: t["finish_time_s"])
    args.config, args.checkpoint = Path(manifest["config"]), Path(manifest["checkpoint"])
    if digest(args.checkpoint) != manifest["checkpoint_sha256"]:
        raise ValueError("Checkpoint changed")
    if digest(args.config) != manifest["config_sha256"]:
        raise ValueError("Configuration changed")
    args.mode, args.variant, args.trials, args.start_race_time_ms = "offline", "neighbors", 1, None
    torch.set_num_threads(2)
    run = resolve_run(experiment_spec(args), base_dir=args.config.parent)
    try:
        _load_checkpoint(run, args.checkpoint)
        replay = run.checkpoint_codec.load(args.checkpoint)["replay_store"]
        policy = NeighborPolicy(
            run.learner.policy(), EXPERIMENTS["neighbors"], build_envelope(replay)
        )
        policy.configure_references(replay)
        if type(policy.base.model.temporal).__name__ != "IdentityTemporalCore":
            raise ValueError("Sampled verification requires a stateless temporal core")
        archive = args.capture / best["capture"]
        if digest(archive) != best["capture_sha256"]:
            raise ValueError("Captured observations changed")
        data = np.load(archive, allow_pickle=False)
        if not np.array_equal(data["q"].argmax(axis=1), data["action"]):
            raise ValueError("Captured actions differ from the captured Q argmax")
        measured = {}
        hooks = []
        modules = dict(policy.base.model.named_modules())
        internal = (
            [
                "encoder.track_conv.0.node_in",
                "encoder.track_conv.0.norms.0",
                "encoder.track_conv.0.norms.1",
                *[f"encoder.backbone.blocks.{i}.expand" for i in range(4)],
                *[f"encoder.backbone.blocks.{i}.project" for i in range(4)],
            ]
            if args.enrich
            else []
        )
        if args.full_path:
            internal += [
                "encoder.spatial_adapter.input_projection",
                *[f"encoder.spatial_adapter.blocks.{i}" for i in range(4)],
                "head.value_stream",
                "head.advantage_stream",
            ]
        enriched = {name: [] for name in internal}
        if args.full_path:
            enriched.update({"fusion": [], "recovery_correction": [], "raw_q": []})
        shapes = {}
        target = args.capture / ("path-tensors.npz" if args.full_path else "internal-tensors.npz")
        if args.enrich and target.exists():
            raise FileExistsError(target)
        for name in [*manifest["stages"], *internal]:

            def record(module, inputs, output, key=name):  # noqa: ANN001, ANN202, PLR0913
                measured[key] = output.detach().cpu().numpy().reshape(-1)
                shapes[key] = list(output.shape[1:])

            hooks.append(modules[name].register_forward_hook(record))
        if args.full_path:

            def record_fusion(module, inputs):  # noqa: ANN001, ANN202
                measured["fusion"] = inputs[0].detach().cpu().numpy().reshape(-1)

            hooks.append(modules["encoder.backbone"].register_forward_pre_hook(record_fusion))
        max_error = 0.0
        samples = (
            np.arange(len(data["action"]))
            if args.enrich
            else np.unique(np.linspace(0, len(data["action"]) - 1, 25, dtype=int))
        )
        for row in samples:
            observation = {
                key.split("/", 1)[1]: torch.from_numpy(data[key][row])
                for key in data.files
                if key.startswith("observation/")
            }
            policy.reset_episode()
            action = policy.act(observation)
            if action != data["action"][row]:
                raise ValueError(f"Recomputed action differs at decision {row}")
            for stage in manifest["stages"]:
                error = float(np.max(np.abs(measured[stage] - data[stage][row])))
                max_error = max(error, max_error)
                np.testing.assert_allclose(measured[stage], data[stage][row], atol=1e-6, rtol=1e-5)
            for stage in internal:
                enriched[stage].append(measured[stage].copy())
            if args.full_path:
                enriched["fusion"].append(measured["fusion"].copy())
                correction = measured["encoder"] - measured["encoder.backbone.blocks.3"]
                enriched["recovery_correction"].append(correction.copy())
                advantage = measured["head.advantage_stream"].reshape(-1, 78)
                value = measured["head.value_stream"].reshape(-1, 1)
                enriched["raw_q"].append(
                    (value + advantage - advantage.mean(axis=-1, keepdims=True)).mean(axis=0)
                )
        for hook in hooks:
            hook.remove()
        report = {
            "sampled_decisions": samples.tolist(),
            "max_activation_error": max_error,
            "all_captured_actions_match_q_argmax": True,
            "sampled_actions_reproduced": True,
            "best_attempt": best["trial_index"] + 1,
            "finish_time_s": best["finish_time_s"],
        }
        if args.enrich:
            np.savez_compressed(target, **{name: np.stack(rows) for name, rows in enriched.items()})
            report.update(
                {
                    "tensor_shapes": shapes,
                    "tensor_sha256": digest(target),
                    "capture_sha256": best["capture_sha256"],
                    "checkpoint_sha256": manifest["checkpoint_sha256"],
                }
            )
            target.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (args.capture / "verification.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
    finally:
        run.logger.close()


if __name__ == "__main__":
    main()
