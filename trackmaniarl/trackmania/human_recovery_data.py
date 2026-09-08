"""Versioned, causal human-recovery demonstration archives."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Literal

import numpy as np

from trackmaniarl.trackmania.demonstration_data import Demonstration

HUMAN_RECOVERY_FORMAT = "trackmaniarl-human-recovery-v1"
MINIMUM_PRE_PERTURBATION_CONTEXT_MS = 950.0
MINIMUM_OBSERVED_PERTURBATION_GAS = 0.75
MAXIMUM_OBSERVED_PERTURBATION_BRAKE = 0.10
MINIMUM_OBSERVED_PERTURBATION_STEER = 0.75
MINIMUM_REQUESTED_DURATION_FRACTION = 0.50
_RECOVERY_ARCHIVE_KEYS = frozenset(
    {
        "format",
        "map_uid",
        "geometry_sha256",
        "action_repeat_frames",
        "decision_interval_ms",
        "control_alignment",
        "frames",
        "actions",
        "controls",
        "finish_time_s",
        "perturbation_start_step",
        "perturbation_steps",
        "takeover_step",
        "target_progress",
        "actual_progress",
        "perturbation_control",
        "requested_perturbation_duration_ms",
        "actual_perturbation_duration_ms",
        "source_checkpoint_sha256",
        "outcome",
    }
)


@dataclass(frozen=True, slots=True)
class RecoveryDemonstration:
    """One completed lap with a forced incident followed by human recovery.

    ``demonstration`` intentionally contains the complete lap, including model and
    perturbation transitions.  Consumers must use ``takeover_step`` as the first
    expert-labelled transition; earlier frames exist only to reconstruct causal
    temporal features.
    """

    demonstration: Demonstration
    perturbation_start_step: int
    perturbation_steps: int
    takeover_step: int
    target_progress: float
    actual_progress: float
    perturbation_control: np.ndarray
    requested_perturbation_duration_ms: float
    actual_perturbation_duration_ms: float
    source_checkpoint_sha256: str
    outcome: Literal["finished"] = "finished"

    def __post_init__(self) -> None:
        _validate_recovery_demonstration(self)


@dataclass(frozen=True, slots=True)
class _RecoveryArchiveFields:
    perturbation_start_step: int
    perturbation_steps: int
    takeover_step: int
    target_progress: float
    actual_progress: float
    perturbation_control: np.ndarray
    requested_duration_ms: float
    actual_duration_ms: float
    checkpoint_sha256: str


def save_recovery_demonstration(path: str | Path, recovery: RecoveryDemonstration) -> Path:
    """Save one completed perturbation-to-human-recovery lap."""

    target = _archive_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = _temporary_archive(target)
    try:
        np.savez_compressed(temporary, **_archive_values(recovery))
        with temporary.open("rb+") as file:
            os.fsync(file.fileno())
        os.replace(temporary, target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return target


def _temporary_archive(target: Path) -> Path:
    with NamedTemporaryFile(
        dir=target.parent,
        prefix=f".{target.stem}-",
        suffix=".tmp.npz",
        delete=False,
    ) as file:
        return Path(file.name)


def load_recovery_demonstration(path: str | Path) -> RecoveryDemonstration:
    """Load and validate a ``human-recovery-v1`` archive."""

    source = Path(path)
    with np.load(source, allow_pickle=False) as data:
        _validate_archive_keys(data)
        _validate_archive_header(data, source)
        return _recovery_from_archive(data)


def _validate_archive_header(data: Any, source: Path) -> None:
    if str(data["format"].item()) != HUMAN_RECOVERY_FORMAT:
        raise ValueError(f"unsupported human-recovery demonstration format: {source}")
    if str(data["outcome"].item()) != "finished":
        raise ValueError("human-recovery archives only accept completed laps")


def _recovery_from_archive(data: Any) -> RecoveryDemonstration:
    fields = _recovery_archive_fields(data)
    return RecoveryDemonstration(
        demonstration=_demonstration_from_archive(data),
        perturbation_start_step=fields.perturbation_start_step,
        perturbation_steps=fields.perturbation_steps,
        takeover_step=fields.takeover_step,
        target_progress=fields.target_progress,
        actual_progress=fields.actual_progress,
        perturbation_control=fields.perturbation_control,
        requested_perturbation_duration_ms=fields.requested_duration_ms,
        actual_perturbation_duration_ms=fields.actual_duration_ms,
        source_checkpoint_sha256=fields.checkpoint_sha256,
        outcome="finished",
    )


def _recovery_archive_fields(data: Any) -> _RecoveryArchiveFields:
    return _RecoveryArchiveFields(
        perturbation_start_step=int(data["perturbation_start_step"].item()),
        perturbation_steps=int(data["perturbation_steps"].item()),
        takeover_step=int(data["takeover_step"].item()),
        target_progress=float(data["target_progress"].item()),
        actual_progress=float(data["actual_progress"].item()),
        perturbation_control=np.asarray(data["perturbation_control"], dtype=np.float32),
        requested_duration_ms=float(data["requested_perturbation_duration_ms"].item()),
        actual_duration_ms=float(data["actual_perturbation_duration_ms"].item()),
        checkpoint_sha256=str(data["source_checkpoint_sha256"].item()),
    )


def _validate_recovery_demonstration(recovery: RecoveryDemonstration) -> None:
    demonstration = recovery.demonstration
    transition_count = len(demonstration.actions)
    start = recovery.perturbation_start_step
    perturbation_end = start + recovery.perturbation_steps
    if start < 0 or recovery.perturbation_steps < 1:
        raise ValueError("recovery perturbation steps must identify a non-empty interval")
    if perturbation_end > recovery.takeover_step or recovery.takeover_step >= transition_count:
        raise ValueError("recovery takeover must follow the perturbation and precede a human label")
    if recovery.outcome != "finished":
        raise ValueError("human-recovery archives only accept completed laps")
    _validate_progress(recovery)
    _validate_perturbation(recovery)
    _validate_provenance(recovery.source_checkpoint_sha256)
    context_ms = float(demonstration.frames[start, 3] - demonstration.frames[0, 3])
    if context_ms < MINIMUM_PRE_PERTURBATION_CONTEXT_MS:
        raise ValueError("human recovery must preserve at least about one second of causal context")


def _validate_progress(recovery: RecoveryDemonstration) -> None:
    values = np.asarray([recovery.target_progress, recovery.actual_progress], dtype=np.float64)
    if not np.isfinite(values).all() or np.any(values < 0.0) or np.any(values > 1.0):
        raise ValueError("recovery target and actual progress must be fractions inside [0, 1]")
    if recovery.actual_progress + 1.0e-6 < recovery.target_progress:
        raise ValueError("actual perturbation progress cannot precede its target")


def _validate_perturbation(recovery: RecoveryDemonstration) -> None:
    control = np.asarray(recovery.perturbation_control)
    if control.shape != (3,) or not np.isfinite(control).all():
        raise ValueError("recovery perturbation control must be a finite [gas, brake, steer]")
    if not _is_strong_perturbation_control(control, float(control[2])):
        raise ValueError("human recovery requires a strong observed gas-and-steer perturbation")
    _validate_perturbation_durations(recovery)
    _validate_observed_perturbation_interval(recovery)


def _validate_perturbation_durations(recovery: RecoveryDemonstration) -> None:
    durations = np.asarray(
        [recovery.requested_perturbation_duration_ms, recovery.actual_perturbation_duration_ms]
    )
    if not np.isfinite(durations).all() or np.any(durations <= 0.0):
        raise ValueError("recovery perturbation durations must be finite and positive")
    minimum_duration = recovery.requested_perturbation_duration_ms * (
        MINIMUM_REQUESTED_DURATION_FRACTION
    )
    if recovery.actual_perturbation_duration_ms + 1.0e-6 < minimum_duration:
        raise ValueError("observed recovery perturbation was too short")


def _validate_observed_perturbation_interval(recovery: RecoveryDemonstration) -> None:
    controls, weights = _observed_perturbation_arrays(recovery)
    direction = float(recovery.perturbation_control[2])
    if not all(_is_strong_perturbation_control(control, direction) for control in controls):
        raise ValueError("recovery perturbation interval does not match observed controls")
    _validate_observed_duration(recovery, weights)
    _validate_observed_control(recovery, controls, weights)


def _observed_perturbation_arrays(
    recovery: RecoveryDemonstration,
) -> tuple[np.ndarray, np.ndarray]:
    start = recovery.perturbation_start_step
    stop = start + recovery.perturbation_steps
    demonstration = recovery.demonstration
    controls = demonstration.controls[start:stop]
    times_ms = demonstration.frames[start : stop + 1, 3].astype(np.float64)
    return controls, np.diff(times_ms)


def _validate_observed_duration(recovery: RecoveryDemonstration, weights: np.ndarray) -> None:
    if not np.isclose(
        float(weights.sum()),
        recovery.actual_perturbation_duration_ms,
        rtol=0.0,
        atol=1.0e-3,
    ):
        raise ValueError("recovery perturbation duration does not match observed frames")


def _validate_observed_control(
    recovery: RecoveryDemonstration, controls: np.ndarray, weights: np.ndarray
) -> None:
    observed_control = np.average(controls.astype(np.float64), axis=0, weights=weights)
    if not np.allclose(observed_control, recovery.perturbation_control, rtol=0.0, atol=1.0e-5):
        raise ValueError("recovery perturbation control does not match observed frames")


def _is_strong_perturbation_control(control: np.ndarray, direction: float) -> bool:
    directed_steer = float(control[2]) * float(np.sign(direction))
    return bool(
        MINIMUM_OBSERVED_PERTURBATION_GAS <= float(control[0]) <= 1.0
        and 0.0 <= float(control[1]) <= MAXIMUM_OBSERVED_PERTURBATION_BRAKE
        and MINIMUM_OBSERVED_PERTURBATION_STEER <= directed_steer <= 1.0
    )


def _validate_provenance(checkpoint_sha256: str) -> None:
    if len(checkpoint_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in checkpoint_sha256
    ):
        raise ValueError("human recovery requires a lowercase SHA-256 checkpoint provenance")


def _archive_path(path: str | Path) -> Path:
    target = Path(path)
    return target if target.suffix.lower() == ".npz" else target.with_suffix(".npz")


def _archive_values(recovery: RecoveryDemonstration) -> dict[str, Any]:
    return _demonstration_archive_values(recovery.demonstration) | _recovery_archive_values(
        recovery
    )


def _demonstration_archive_values(demonstration: Demonstration) -> dict[str, Any]:
    return {
        "format": np.asarray(HUMAN_RECOVERY_FORMAT),
        "map_uid": np.asarray(demonstration.map_uid),
        "geometry_sha256": np.asarray(demonstration.geometry_sha256),
        "action_repeat_frames": np.asarray(demonstration.action_repeat_frames, dtype=np.int32),
        "decision_interval_ms": np.asarray(demonstration.decision_interval_ms or 0.0),
        "control_alignment": np.asarray(demonstration.control_alignment),
        "frames": np.asarray(demonstration.frames, dtype=np.float32),
        "actions": np.asarray(demonstration.actions, dtype=np.int64),
        "controls": np.asarray(demonstration.controls, dtype=np.float32),
        "finish_time_s": np.asarray(demonstration.finish_time_s, dtype=np.float64),
    }


def _recovery_archive_values(recovery: RecoveryDemonstration) -> dict[str, Any]:
    requested = np.asarray(recovery.requested_perturbation_duration_ms, dtype=np.float64)
    actual = np.asarray(recovery.actual_perturbation_duration_ms, dtype=np.float64)
    return {
        "perturbation_start_step": np.asarray(recovery.perturbation_start_step, dtype=np.int64),
        "perturbation_steps": np.asarray(recovery.perturbation_steps, dtype=np.int64),
        "takeover_step": np.asarray(recovery.takeover_step, dtype=np.int64),
        "target_progress": np.asarray(recovery.target_progress, dtype=np.float64),
        "actual_progress": np.asarray(recovery.actual_progress, dtype=np.float64),
        "perturbation_control": np.asarray(recovery.perturbation_control, dtype=np.float32),
        "requested_perturbation_duration_ms": requested,
        "actual_perturbation_duration_ms": actual,
        "source_checkpoint_sha256": np.asarray(recovery.source_checkpoint_sha256),
        "outcome": np.asarray(recovery.outcome),
    }


def _validate_archive_keys(data: Any) -> None:
    missing = _RECOVERY_ARCHIVE_KEYS - set(data.files)
    if missing:
        raise ValueError(f"human-recovery demonstration is missing keys: {sorted(missing)}")


def _demonstration_from_archive(data: Any) -> Demonstration:
    return Demonstration(
        map_uid=str(data["map_uid"].item()),
        geometry_sha256=str(data["geometry_sha256"].item()),
        action_repeat_frames=int(data["action_repeat_frames"].item()),
        frames=np.asarray(data["frames"], dtype=np.float32),
        actions=np.asarray(data["actions"], dtype=np.int64),
        controls=np.asarray(data["controls"], dtype=np.float32),
        finish_time_s=float(data["finish_time_s"].item()),
        decision_interval_ms=float(data["decision_interval_ms"].item()) or None,
        control_alignment=str(data["control_alignment"].item()),
    )
