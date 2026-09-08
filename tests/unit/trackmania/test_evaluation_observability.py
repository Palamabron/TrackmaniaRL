from __future__ import annotations

import pytest

from trackmaniarl.experiments.evaluation import EvaluationResult
from trackmaniarl.trackmania.evaluation_observability import EvaluationObservability


def _result() -> EvaluationResult:
    return EvaluationResult(False, None, False, 0.0, 0.0, 0.0)


def test_step_race_time_measurements_are_counted_when_every_step_is_valid() -> None:
    observability = EvaluationObservability()
    observability.record({"step_race_time_ms": 40.0}, 1.0)
    observability.record({"step_race_time_ms": 60.0}, 1.0)

    result = observability.annotated_result(_result(), step_count=2)

    assert result.step_race_time_measurement_count == 2
    assert result.step_race_time_measurements_valid is True
    assert result.step_race_time_ms_p99 == 60.0
    assert result.step_race_time_ms_max == 60.0


@pytest.mark.parametrize("invalid", [None, 0.0, -1.0, float("nan"), float("inf"), "50"])
def test_step_race_time_measurements_reject_every_invalid_individual_step(
    invalid: object,
) -> None:
    observability = EvaluationObservability()
    observability.record({"step_race_time_ms": 50.0}, 1.0)
    observability.record({"step_race_time_ms": invalid}, 1.0)

    result = observability.annotated_result(_result(), step_count=2)

    assert result.step_race_time_measurement_count == 1
    assert result.step_race_time_measurements_valid is False
    assert result.step_race_time_ms_p99 == 50.0
    assert result.step_race_time_ms_max == 50.0


def test_finish_flag_at_same_race_clock_is_a_measured_zero_interval() -> None:
    observability = EvaluationObservability()
    observability.record({"step_race_time_ms": 50.0}, 1.0)
    observability.record(
        {"step_race_time_ms": 0.0, "termination_reason": "finished", "telemetry_health": "ok"}, 1.0
    )
    result = observability.annotated_result(_result(), step_count=2)
    assert result.step_race_time_measurement_count == 2
    assert result.step_race_time_measurements_valid is True
    assert result.step_race_time_ms_max == 50.0


@pytest.mark.parametrize("value", [-1.0, False, None, float("nan")])
def test_finish_does_not_excuse_invalid_or_regressing_clock(value: object) -> None:
    observability = EvaluationObservability()
    observability.record({"step_race_time_ms": 50.0}, 1.0)
    observability.record(
        {"step_race_time_ms": value, "termination_reason": "finished", "telemetry_health": "ok"},
        1.0,
    )
    result = observability.annotated_result(_result(), step_count=2)
    assert result.step_race_time_measurements_valid is False
