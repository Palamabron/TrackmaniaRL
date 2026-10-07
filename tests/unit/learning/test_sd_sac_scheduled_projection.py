"""Scheduled pilots must neither start early nor restart an old queue."""

from datetime import UTC, datetime

import pytest

from experiments.tmrl_test_comparison import launch_sd_sac_projection as pilot


def schedule() -> dict[str, str]:
    return {"not_before": pilot.NOT_BEFORE, "latest_start": pilot.LATEST_START}


@pytest.mark.parametrize("time", ["2026-10-07T23:30:00+00:00", "2026-10-08T01:30:00+02:00"])
def test_start_at_the_same_authorized_instant_in_both_timezones(time: str) -> None:
    pilot.check_start_window(schedule(), datetime.fromisoformat(time))


@pytest.mark.parametrize(
    ("time", "reason"),
    [
        ("2026-10-07T23:29:59+00:00", "too early"),
        ("2026-10-07T23:45:01+00:00", "missed"),
        ("2026-10-08T23:30:00+00:00", "missed"),
    ],
)
def test_start_outside_the_window_fails_closed(time: str, reason: str) -> None:
    with pytest.raises(RuntimeError, match=reason):
        pilot.check_start_window(schedule(), datetime.fromisoformat(time))


def test_schedule_cannot_be_extended_by_the_plan() -> None:
    changed = schedule()
    changed["latest_start"] = "2026-10-08T23:45:00+00:00"
    with pytest.raises(RuntimeError, match="changed"):
        pilot.check_start_window(changed, datetime(2026, 10, 7, 23, 30, tzinfo=UTC))


def test_naive_clock_rejected() -> None:
    with pytest.raises(ValueError, match="timezone aware"):
        pilot.check_start_window(schedule(), datetime(2026, 10, 8, 1, 30))
