from __future__ import annotations

import pytest

from trackmaniarl.distributed.actor_metrics import ControlUsageTracker


def test_control_usage_tracker_keeps_timing_when_control_metrics_are_absent() -> None:
    tracker = ControlUsageTracker()
    tracker.record(
        {
            "control_gas": 1.0,
            "control_brake": 0.0,
            "control_steer": 0.0,
            "step_race_time_ms": 50.0,
        }
    )
    tracker.record({"step_race_time_ms": 500.0})

    summary = tracker.summary()

    assert summary["step_race_time_ms_max"] == 500.0
    assert summary["step_race_time_measurement_count"] == 2.0
    assert summary["step_race_time_measurements_valid"] == 1.0


@pytest.mark.parametrize(
    "invalid_step",
    [
        {},
        {"step_race_time_ms": 0.0},
        {"step_race_time_ms": -1.0},
        {"step_race_time_ms": float("nan")},
        {"step_race_time_ms": float("inf")},
    ],
)
def test_control_usage_tracker_marks_invalid_individual_step_timing(
    invalid_step: dict[str, float],
) -> None:
    tracker = ControlUsageTracker()
    tracker.record({"step_race_time_ms": 50.0})
    tracker.record(invalid_step)

    summary = tracker.summary()

    assert summary["step_race_time_ms_max"] == 50.0
    assert summary["step_race_time_measurement_count"] == 1.0
    assert summary["step_race_time_measurements_valid"] == 0.0
