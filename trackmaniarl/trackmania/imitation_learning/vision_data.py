"""Validated RGB/action episode archives for offline camera behavior cloning."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from trackmaniarl.trackmania.imitation_learning._data_types import (
    BehaviorCloningLap,
    RecoveryContract,
)
from trackmaniarl.trackmania.imitation_learning.vision import VisionBehaviorCloningPipeline

VISION_DEMONSTRATION_FORMAT = "trackmaniarl-vision-demo-v1"


@dataclass(frozen=True, slots=True)
class VisionDemonstration:
    """One complete episode with each RGB frame preceding its canonical action."""

    frames: np.ndarray[Any, Any]
    actions: np.ndarray[Any, Any]
    timestamps_ms: np.ndarray[Any, Any]
    contract: RecoveryContract
    finish_time_s: float
    telemetry: np.ndarray[Any, Any] | None = None

    def validate(self) -> None:
        if self.frames.dtype != np.uint8 or self.frames.ndim != 4 or self.frames.shape[-1] != 3:
            raise ValueError("vision demo frames must be uint8 (steps, height, width, 3)")
        if min(self.frames.shape[:3]) < 1:
            raise ValueError("vision demo frames must not be empty")
        count = len(self.frames)
        if self.telemetry is not None:
            if (
                self.telemetry.shape != (count, 33)
                or self.telemetry.dtype.kind not in "fiu"
                or not np.isfinite(self.telemetry).all()
            ):
                raise ValueError(
                    "paired demo requires finite numeric telemetry with shape (steps, 33)"
                )
            if not np.array_equal(self.telemetry[:, 3], self.timestamps_ms):
                raise ValueError("paired telemetry race times must match image timestamps")
        if self.actions.shape != (count,) or self.actions.dtype.kind not in "iu":
            raise ValueError("vision demo requires one integer canonical action per frame")
        if np.any(self.actions < 0) or np.any(self.actions >= 78):
            raise ValueError("vision demo actions must be canonical IDs in [0, 78)")
        if self.timestamps_ms.shape != (count,) or self.timestamps_ms.dtype.kind not in "fiu":
            raise ValueError("vision demo requires one numeric timestamp per frame")
        if (
            not np.isfinite(self.timestamps_ms).all()
            or np.any(self.timestamps_ms < 0)
            or np.any(np.diff(self.timestamps_ms.astype(np.float64)) <= 0)
        ):
            raise ValueError("vision demo timestamps must be finite, nonnegative and increasing")
        if not np.isfinite(self.finish_time_s) or self.finish_time_s <= 0:
            raise ValueError("vision demo requires a finite positive finish time")
        if self.timestamps_ms[-1] >= self.finish_time_s * 1000:
            raise ValueError("vision demo frames must precede the episode finish")


def save_vision_demonstration(path: str | Path, demonstration: VisionDemonstration) -> None:
    """Save a complete episode without pickle or overwriting an existing file."""
    demonstration.validate()
    metadata = {
        "format": VISION_DEMONSTRATION_FORMAT
        if demonstration.telemetry is None
        else "trackmaniarl-paired-demo-v1",
        "contract": asdict(demonstration.contract),
        "finish_time_s": demonstration.finish_time_s,
    }
    target = Path(path)
    stream = target.open("xb")
    extra: dict[str, Any] = (
        {} if demonstration.telemetry is None else {"telemetry": demonstration.telemetry}
    )
    try:
        with stream:
            np.savez_compressed(
                stream,
                frames=demonstration.frames,
                actions=demonstration.actions,
                timestamps_ms=demonstration.timestamps_ms,
                metadata=json.dumps(metadata),
                **extra,
            )
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def load_vision_demonstration(path: str | Path) -> VisionDemonstration:
    with np.load(path, allow_pickle=False) as data:
        required = {"frames", "actions", "timestamps_ms", "metadata"}
        if set(data.files) not in (required, required | {"telemetry"}):
            raise ValueError("expected a vision demonstration archive with RGB frames and actions")
        metadata = json.loads(str(data["metadata"].item()))
        expected_format = (
            "trackmaniarl-paired-demo-v1"
            if "telemetry" in data.files
            else VISION_DEMONSTRATION_FORMAT
        )
        if not isinstance(metadata, dict) or metadata.get("format") != expected_format:
            raise ValueError("unsupported vision demonstration format")
        if set(metadata) != {"format", "contract", "finish_time_s"}:
            raise ValueError("invalid vision demonstration metadata")
        demonstration = VisionDemonstration(
            data["frames"],
            data["actions"],
            data["timestamps_ms"],
            RecoveryContract(**metadata["contract"]),
            float(metadata["finish_time_s"]),
            data["telemetry"] if "telemetry" in data.files else None,
        )
    demonstration.validate()
    return demonstration


@dataclass(frozen=True, slots=True)
class VisionLapLoadRequest:
    paths: Sequence[Path]
    pipeline: VisionBehaviorCloningPipeline
    action_ids: tuple[int, ...]
    contract: RecoveryContract
    previous_action_conditioning: bool = False


def load_vision_behavior_cloning_laps(request: VisionLapLoadRequest) -> list[BehaviorCloningLap]:
    if len(request.paths) < 3:
        raise ValueError("vision BC requires at least three complete demonstration episodes")
    laps: list[BehaviorCloningLap] = []
    seen: set[bytes] = set()
    for path in request.paths:
        demonstration = load_vision_demonstration(path)
        if request.pipeline.expects_telemetry != (demonstration.telemetry is not None):
            raise ValueError("BC pipeline and demonstration sensor modalities must match")
        if demonstration.contract != request.contract:
            raise ValueError(f"vision demo {path} map, geometry or timing contract does not match")
        # Copies of one episode must not leak into both training and validation.
        digest = hashlib.sha256()
        digest.update(str(demonstration.frames.shape).encode())
        for values in (demonstration.frames, demonstration.actions.astype(np.int64)):
            digest.update(np.ascontiguousarray(values).tobytes())
        identity = digest.digest()
        if identity in seen:
            raise ValueError("duplicate vision episode would leak across the dataset split")
        seen.add(identity)
        laps.append(_vision_lap(request, demonstration, path))
    return laps


def _vision_lap(
    request: VisionLapLoadRequest,
    demonstration: VisionDemonstration,
    path: Path,
) -> BehaviorCloningLap:
    mapping = {action: index for index, action in enumerate(request.action_ids)}
    if any(int(action) not in mapping for action in demonstration.actions):
        raise ValueError(f"vision demo {path} contains an action outside compact action IDs")
    request.pipeline.reset_episode()
    previous = len(mapping)
    observations: list[dict[str, torch.Tensor]] = []
    labels: list[int] = []
    try:
        for index, (frame, action) in enumerate(
            zip(demonstration.frames, demonstration.actions, strict=True)
        ):
            raw = (
                frame
                if demonstration.telemetry is None
                else {"images": frame, "telemetry": demonstration.telemetry[index]}
            )
            observation = request.pipeline.transform_observation(raw)
            observation["expert_previous_action"] = torch.tensor(previous, dtype=torch.long)
            if request.previous_action_conditioning:
                observation["previous_action"] = torch.tensor(previous, dtype=torch.long)
            observations.append(observation)
            previous = mapping[int(action)]
            labels.append(previous)
    finally:
        request.pipeline.reset_episode()
    return BehaviorCloningLap(
        tuple(observations), torch.tensor(labels), source_id=str(path.resolve())
    )
