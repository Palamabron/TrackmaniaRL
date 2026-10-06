"""Recorded-return arithmetic, without building a model or running a learner."""

from dataclasses import replace

import pytest

from experiments.tmrl_test_comparison.sd_sac_calibration import (
    RecordedValue,
    recorded_return_report,
)


def test_soft_returns_include_future_entropy_and_zero_terminal_bootstrap() -> None:
    rows = [
        RecordedValue(0, 1, 7, 3, 3, False),
        RecordedValue(1, 2, 2, 2, 2, True),
    ]
    report = recorded_return_report({"episode": rows}, gamma=0.5, alpha=1)
    # Q0 = 1 + .5 * (2 + H1), excludes H0. Q1 = reward1, excludes terminal entropy.
    start = report["groups"]["episode_start"]
    assert start["behavior_soft_return_mean"] == 3
    assert start["reward_return_mean"] == 2
    assert start["soft_return_rmse"] == 0
    assert report["groups"]["terminal"]["soft_return_rmse"] == 0
    assert report["complete_episodes"] == 1
    assert report["driving_gate_passed"] is False


@pytest.mark.parametrize("reason", ["missing_start", "missing_tail", "truncated", "gap"])
def test_incomplete_episodes_are_excluded_without_fabricating_a_return(reason: str) -> None:
    first = RecordedValue(0, 1, 0, 3, 3, False)
    last = RecordedValue(1, 2, 0, 2, 2, True)
    rows = {
        "missing_start": [last],
        "missing_tail": [first],
        "truncated": [first, replace(last, terminated=False, truncated=True)],
        "gap": [first, replace(last, step=2)],
    }[reason]
    report = recorded_return_report({"incomplete": rows}, gamma=0.99, alpha=0.1)
    assert report["complete_episodes"] == 0
    assert report["excluded_episodes"] == ["incomplete"]
    assert report["groups"] == {}


def test_report_keeps_selected_action_errors_and_strata_separate() -> None:
    report = recorded_return_report(
        {"stop": [RecordedValue(0, -1, 0, 4, 6, True, stratum="full_brake")]},
        gamma=0.99,
        alpha=0.1,
    )
    assert report["groups"]["full_brake"]["soft_return_bias"] == 6
    assert report["groups"]["all"]["states"] == 1
    assert report["comparison_target"] == "recorded_behavior_soft_return_proxy"


@pytest.mark.parametrize("field", ["reward", "behavior_entropy", "q1", "q2"])
def test_nonfinite_records_rejected(field: str) -> None:
    row = replace(RecordedValue(0, 1, 0, 1, 1, True), **{field: float("nan")})
    with pytest.raises(ValueError, match="Invalid recorded values"):
        recorded_return_report({"episode": [row]}, gamma=0.99, alpha=0.1)
