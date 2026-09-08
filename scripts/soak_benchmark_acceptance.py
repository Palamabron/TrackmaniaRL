"""Evidence-backed acceptance rules for a final soak benchmark."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, replace
from statistics import fmean, median
from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING or __package__:
    from scripts.soak_types import integer, number, string
else:
    from soak_types import integer, number, string


@dataclass(frozen=True, slots=True)
class AcceptanceThresholds:
    trials_per_map: int
    minimum_finish_rate: float
    target_median_s: float
    target_mean_s: float | None
    max_step_race_time_ms: float | None


@dataclass(frozen=True, slots=True)
class TrialAcceptance:
    passed: bool
    finished: int
    median_s: float | None
    mean_s: float | None
    max_step_race_time_ms: float | None
    step_race_time_measurements_valid: bool
    step_race_time_measurement_count: int
    step_race_time_expected_measurement_count: int


@dataclass(slots=True)
class _StepRaceTimeEvidence:
    values: list[float] = field(default_factory=list)
    measurement_count: int = 0
    expected_measurement_count: int = 0
    valid: bool = True


def _trial_acceptance(
    trials: list[dict[str, object]],
    suite: dict[str, object],
    assets: list[dict[str, object]],
) -> TrialAcceptance:
    thresholds = _acceptance_thresholds(suite)
    expected = _expected_trials(assets, thresholds.trials_per_map)
    finished_times = _finished_times(trials)
    acceptance = _trial_statistics(trials, finished_times)
    passed = _acceptance_passed((_observed_trials(trials), expected), acceptance, thresholds)
    return replace(acceptance, passed=passed)


def _trial_statistics(
    trials: list[dict[str, object]], finished_times: list[float]
) -> TrialAcceptance:
    (
        maximum_step_ms,
        runtime_measurements_valid,
        measurement_count,
        expected_measurement_count,
    ) = _step_race_time_statistics(trials)
    return TrialAcceptance(
        False,
        len(finished_times),
        median(finished_times) if finished_times else None,
        fmean(finished_times) if finished_times else None,
        maximum_step_ms,
        runtime_measurements_valid,
        measurement_count,
        expected_measurement_count,
    )


def _acceptance_passed(
    counts: tuple[Counter[str], Counter[str]],
    acceptance: TrialAcceptance,
    thresholds: AcceptanceThresholds,
) -> bool:
    observed, expected = counts
    finish_rate = acceptance.finished / sum(expected.values()) if expected else 0.0
    return (
        observed == expected
        and finish_rate >= thresholds.minimum_finish_rate
        and acceptance.median_s is not None
        and acceptance.median_s < thresholds.target_median_s
        and _mean_accepted(acceptance.mean_s, thresholds.target_mean_s)
        and _runtime_accepted(acceptance, thresholds.max_step_race_time_ms)
    )


def _mean_accepted(mean_s: float | None, target_mean_s: float | None) -> bool:
    return target_mean_s is None or (mean_s is not None and mean_s < target_mean_s)


def _runtime_accepted(acceptance: TrialAcceptance, target_ms: float | None) -> bool:
    maximum_ms = acceptance.max_step_race_time_ms
    return target_ms is None or (
        acceptance.step_race_time_measurements_valid
        and maximum_ms is not None
        and maximum_ms <= target_ms
    )


def _step_race_time_statistics(
    trials: list[dict[str, object]],
) -> tuple[float | None, bool, int, int]:
    evidence = _StepRaceTimeEvidence()
    for index, trial in enumerate(trials):
        _record_step_race_time_evidence(evidence, trial, index)
    return (
        max(evidence.values) if evidence.values else None,
        evidence.valid,
        evidence.measurement_count,
        evidence.expected_measurement_count,
    )


def _record_step_race_time_evidence(
    evidence: _StepRaceTimeEvidence, trial: dict[str, object], index: int
) -> None:
    _record_trial_maximum(evidence, trial, index)
    _record_trial_measurement_counts(evidence, trial)


def _record_trial_maximum(
    evidence: _StepRaceTimeEvidence, trial: dict[str, object], index: int
) -> None:
    maximum = trial.get("step_race_time_ms_max")
    if maximum is None:
        evidence.valid = False
        return
    value = number(maximum, f"evaluation.json.trials[{index}].step_race_time_ms_max")
    evidence.values.append(value)
    evidence.valid = evidence.valid and value > 0.0


def _record_trial_measurement_counts(
    evidence: _StepRaceTimeEvidence, trial: dict[str, object]
) -> None:
    steps = trial.get("steps")
    count = trial.get("step_race_time_measurement_count")
    if _positive_integer(steps):
        evidence.expected_measurement_count += steps
    else:
        evidence.valid = False
    if _nonnegative_integer(count):
        evidence.measurement_count += count
    else:
        evidence.valid = False
    evidence.valid = evidence.valid and _trial_measurements_valid(trial, steps, count)


def _trial_measurements_valid(trial: dict[str, object], steps: object, count: object) -> bool:
    return count == steps and trial.get("step_race_time_measurements_valid") is True


def _positive_integer(value: object) -> TypeGuard[int]:
    return not isinstance(value, bool) and isinstance(value, int) and value > 0


def _nonnegative_integer(value: object) -> TypeGuard[int]:
    return not isinstance(value, bool) and isinstance(value, int) and value >= 0


def _finished_times(trials: list[dict[str, object]]) -> list[float]:
    return [
        number(trial.get("finish_time_s"), "finished trial finish_time_s")
        for trial in trials
        if trial.get("finished") is True
    ]


def _acceptance_thresholds(suite: dict[str, object]) -> AcceptanceThresholds:
    return AcceptanceThresholds(
        integer(suite.get("trials_per_map"), "evaluation trials_per_map"),
        number(suite.get("min_finish_rate"), "evaluation min_finish_rate"),
        number(suite.get("target_median_s"), "evaluation target_median_s"),
        _optional_number(suite.get("target_mean_s"), "evaluation target_mean_s"),
        _optional_number(suite.get("max_step_race_time_ms"), "evaluation max_step_race_time_ms"),
    )


def _optional_number(value: object, label: str) -> float | None:
    return None if value is None else number(value, label)


def _expected_trials(assets: list[dict[str, object]], trials_per_map: int) -> Counter[str]:
    return Counter(
        {string(asset.get("map_id"), "evaluation asset map_id"): trials_per_map for asset in assets}
    )


def _observed_trials(trials: list[dict[str, object]]) -> Counter[str]:
    return Counter(string(trial.get("map_id"), "benchmark trial map_id") for trial in trials)
