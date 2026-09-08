"""Safety checks that keep recovery archives free of respawn discontinuities."""

from __future__ import annotations

import numpy as np

from trackmaniarl.trackmania.human_recovery_recording_types import (
    HumanRecoveryRecordingRequest,
    RecoveryAttemptError,
)

_POSITION_SLACK_M = 5.0
_KINEMATIC_FACTOR = 3.0
_ACCELERATION_ALLOWANCE_MPS2 = 150.0


def require_continuous_lap(
    request: HumanRecoveryRecordingRequest, current: np.ndarray, following: np.ndarray
) -> None:
    if float(following[3]) <= float(current[3]):
        raise RecoveryAttemptError("restart or non-advancing race timer discarded the partial lap")
    displacement = _position_displacement(request, current, following)
    if displacement > _maximum_plausible_displacement(request, current, following):
        raise RecoveryAttemptError(
            f"respawn or teleport discarded the partial lap ({displacement:.1f} m jump)"
        )


def _position_displacement(
    request: HumanRecoveryRecordingRequest, current: np.ndarray, following: np.ndarray
) -> float:
    indices = list(request.environment.config.position_indices)
    return float(np.linalg.norm(following[indices] - current[indices]))


def _maximum_plausible_displacement(
    request: HumanRecoveryRecordingRequest, current: np.ndarray, following: np.ndarray
) -> float:
    elapsed_s = float(following[3] - current[3]) / 1_000.0
    average_speed = (_frame_speed_mps(request, current) + _frame_speed_mps(request, following)) / 2
    travel = _KINEMATIC_FACTOR * average_speed * elapsed_s
    acceleration = 0.5 * _ACCELERATION_ALLOWANCE_MPS2 * elapsed_s**2
    return _POSITION_SLACK_M + travel + acceleration


def _frame_speed_mps(request: HumanRecoveryRecordingRequest, frame: np.ndarray) -> float:
    config = request.environment.config
    velocity = frame[list(config.velocity_indices)]
    vector_speed = float(np.linalg.norm(velocity)) * float(config.velocity_to_mps_scale)
    return max(abs(float(frame[16])), vector_speed)
