"""Inspect whether a historical benchmark can support an activation film."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from experiments.sub37.policy import replay_columns
from trackmaniarl.core.builtins import TorchCheckpointCodec


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def audit(benchmark: Path, checkpoint: Path, video: Path) -> dict:
    experiment = json.loads((benchmark / "experiment.json").read_text(encoding="utf-8"))
    checkpoint_hash = digest(checkpoint)
    if checkpoint_hash != experiment["sha256"]:
        raise ValueError("Checkpoint does not match the benchmark's recorded SHA-256")
    episodes = json.loads((benchmark / "policy-traces.json").read_text(encoding="utf-8"))
    finished = [item for item in episodes if item.get("finished")]
    if not finished:
        raise ValueError("No recorded finish in this benchmark")
    best = min(finished, key=lambda item: item["finish_time_s"])
    trace = np.asarray(best["trace"], dtype=np.float64)
    if trace.ndim != 2 or trace.shape[1] != 4 or not np.isfinite(trace).all():
        raise ValueError("Expected the historical four-column policy trace")
    state = TorchCheckpointCodec().load(checkpoint)
    columns = replay_columns(state["replay_store"])
    physics = np.asarray(columns["physics"])
    pairs = set(zip(physics[:, 3].tolist(), physics[:, 0].tolist(), strict=True))
    matches = sum((row[0], row[1]) in pairs for row in trace)
    return {
        "status": "blocked_missing_inference_inputs",
        "benchmark": str(benchmark.resolve()),
        "video": str(video.resolve()),
        "video_sha256": digest(video),
        "checkpoint": str(checkpoint.resolve()),
        "checkpoint_sha256": checkpoint_hash,
        "variant": experiment["experiment"]["name"],
        "finished_attempts": len(finished),
        "best_attempt_one_based": best["trial_index"] + 1,
        "best_telemetry_time_s": best["finish_time_s"],
        "decisions": len(trace),
        "recorded_columns": ["physics[3]", "physics[0]", "context[0]", "action"],
        "required_observation_shapes": {
            key: list(value.shape[1:]) for key, value in columns.items()
        },
        "required_scalar_inputs": sum(int(np.prod(value.shape[1:])) for value in columns.values()),
        "decisions_with_exact_progress_speed_pair_in_training_replay": matches,
        "activation_values_recorded": False,
        "per_decision_video_timestamps_recorded": False,
        "warning": (
            "Matching two features would not establish an identical observation. "
            "The source checkpoint predates evaluation. Its replay is not a recording "
            "of these benchmark attempts. Missing features must not be fabricated. "
            "Video hash identifies bytes but does not verify the lap's visual boundaries."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark", type=Path)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("video", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.benchmark, args.checkpoint, args.video)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
