"""Record a fixed series with the activations that actually selected each action."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import torch

from experiments.sub37.audit_activation_sources import digest
from experiments.sub37.neighbors import NeighborPolicy
from experiments.sub37.policy import EXPERIMENTS, build_envelope
from experiments.sub37.runner import experiment_spec
from trackmaniarl.commands.evaluation import _load_checkpoint
from trackmaniarl.core.runtime import resolve_run
from trackmaniarl.trackmania.actions import build_brake_tap_action_table

STAGES = [
    "encoder.track_conv.0",
    "encoder.track_conv",
    "encoder.physics_proj",
    "encoder.context_adapter",
    "encoder.spatial_adapter",
    "encoder.recovery_adapter",
    "encoder.backbone.input_projection",
    *[f"encoder.backbone.blocks.{i}" for i in range(4)],
    "encoder",
]


def finite_json(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: finite_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_json(v) for v in value]
    return value


class ActivationCapture:
    def __init__(self, run: Any, policy: Any, output: Path) -> None:
        self.run, self.policy, self.output = run, policy, output
        self.pending = {}
        self.rows = []
        self.handles = []
        modules = dict(policy.base.model.named_modules())
        for name in STAGES:
            self.handles.append(modules[name].register_forward_hook(self.hook(name)))
        original_values = policy._values

        def values(features: Any, progress: float) -> Any:
            result = original_values(features, progress)
            self.pending["q"] = result.detach().clone()
            return result

        self.original_values = original_values
        policy._values = values
        self.original_step = run.evaluator._take_step
        self.original_episode = run.evaluator._evaluate_episode
        run.evaluator._take_step = self.step
        run.evaluator._evaluate_episode = self.episode

    def hook(self, name: str) -> Any:
        def record(module: Any, inputs: Any, output: Any) -> None:
            self.pending[name] = output.detach().clone()

        return record

    def step(self, loop: Any) -> Any:
        self.pending = {}
        started = time.time()
        raw = np.asarray(loop.observation).copy()
        observations = {k: v.detach().cpu().numpy().copy() for k, v in loop.prepared.items()}
        step = self.original_step(loop)
        # Transfer after environment.step so GPU copies do not delay control application.
        captured = {k: v.cpu().numpy().reshape(-1) for k, v in self.pending.items()}
        if set(captured) != {*STAGES, "q"}:
            raise RuntimeError("A decision did not execute all instrumented modules")
        self.rows.append(
            {
                "utc": started,
                "race_ms": float(raw[3]),
                "raw": raw,
                "action": int(step.action),
                "progress": float(loop.prepared["physics"][3]),
                "speed_kmh": float(raw[16]) * 3.6,
                **{f"observation/{k}": v for k, v in observations.items()},
                **captured,
            }
        )
        return step

    def episode(self, request: Any) -> Any:
        self.rows = []
        result = self.original_episode(request)
        if not self.rows:
            raise RuntimeError("No inference captured for the attempt")
        arrays = {k: np.stack([row[k] for row in self.rows]) for k in self.rows[0]}
        target = self.output / f"trial-{result.trial_index + 1:02}.npz"
        with target.open("xb") as stream:
            np.savez_compressed(stream, **arrays)
        payload = asdict(result)
        payload["capture"] = target.name
        payload["capture_sha256"] = digest(target)
        with (self.output / "trials.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(finite_json(payload), allow_nan=False) + "\n")
        print(
            f"Attempt {result.trial_index + 1}: {result.finish_time_s}s, "
            f"{len(self.rows)} decisions",
            flush=True,
        )
        return result

    def close(self) -> None:
        for handle in self.handles:
            handle.remove()
        self.policy._values = self.original_values
        self.run.evaluator._take_step = self.original_step
        self.run.evaluator._evaluate_episode = self.original_episode


def main() -> None:
    import imageio_ffmpeg

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trials", type=int, default=5)
    args = parser.parse_args()
    os.environ.setdefault("WANDB_MODE", "disabled")
    args.output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, args.output / "capture-source.py")
    args.config = args.config.resolve(strict=True)
    args.checkpoint = args.checkpoint.resolve(strict=True)
    args.variant, args.mode, args.start_race_time_ms = "neighbors", "benchmark", None
    torch.set_num_threads(2)
    run = resolve_run(experiment_spec(args), base_dir=args.config.parent)
    capture = None
    try:
        _load_checkpoint(run, args.checkpoint)
        replay = run.checkpoint_codec.load(args.checkpoint)["replay_store"]
        policy = NeighborPolicy(
            run.learner.policy(), EXPERIMENTS["neighbors"], build_envelope(replay)
        )
        policy.configure_references(replay)
        capture = ActivationCapture(run, policy, args.output)
        command = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-n",
            "-debug_ts",
            "-f",
            "gdigrab",
            "-framerate",
            "30",
            "-i",
            "title=Trackmania",
            "-an",
            "-vf",
            "scale=1280:-2",
            "-c:v",
            "libx264",
            "-threads",
            "2",
            "-preset",
            "ultrafast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(args.output / "source.mkv"),
        ]
        metadata = {
            "checkpoint": str(args.checkpoint),
            "checkpoint_sha256": digest(args.checkpoint),
            "config": str(args.config),
            "config_sha256": digest(args.config),
            "capture_code_sha256": digest(Path(__file__)),
            "variant": "V107I + map-specific neighbors",
            "stages": STAGES,
            "action_table": [a.tolist() for a in build_brake_tap_action_table()[1]],
            "planned_trials": args.trials,
            "recording_command": command,
            "torch_version": torch.__version__,
            "run_directory": str(run.run_dir),
        }
        (args.output / "manifest.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        (args.output / "model.txt").write_text(str(policy.base.model), encoding="utf-8")
        (args.output / "config.json").write_text(
            run.spec.model_dump_json(indent=2), encoding="utf-8"
        )
        with (args.output / "ffmpeg.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=log,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            try:
                time.sleep(2)
                if process.poll() is not None:
                    raise RuntimeError("Recorder failed, inspect ffmpeg.log")
                run.evaluator.evaluate(policy)
                time.sleep(2)
            finally:
                try:
                    process.communicate(b"q\n", timeout=20)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                    raise RuntimeError("Recording did not finalize") from None
            if process.returncode:
                raise RuntimeError("Recorder failed")
        print(f"Capture complete: {args.output.resolve()}", flush=True)
    finally:
        if capture is not None:
            capture.close()
        run.logger.close()


if __name__ == "__main__":
    main()
