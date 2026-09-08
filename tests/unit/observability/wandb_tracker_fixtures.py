from __future__ import annotations

from trackmaniarl.experiments.evaluation import EvaluationResult


def finished_evaluation() -> EvaluationResult:
    return EvaluationResult(
        True,
        35.0,
        False,
        4.0,
        1.0,
        50.0,
        steps=2,
        controller_apply_ms=2.25,
        telemetry_wait_ms=49.0,
        control_brake_tap_fraction=0.5,
        step_race_time_ms_p99=52.0,
        step_race_time_ms_max=60.0,
        step_race_time_measurement_count=2,
        step_race_time_measurements_valid=True,
        telemetry_skipped_frames_total=3,
    )
