"""The follow-up candidate may change only actor LR and descriptive identity."""

import copy
from datetime import datetime
from typing import Any

import pytest

from experiments.tmrl_test_comparison.launch_sd_sac_projected_actor_lr import (
    LATEST_START,
    NOT_BEFORE,
    check_start_window,
    validate_scope,
)


def baseline() -> dict[str, Any]:
    return {
        "run_id": "previous",
        "metadata": {"automatic_full_training": False},
        "components": {
            "learner": {"kwargs": {"actor_learning_rate": 0.0001, "entropy_coefficient_min": 0.01}}
        },
        "reward": {"terminal": -2},
        "training": {"total_transitions": 145408},
    }


def candidate() -> dict[str, Any]:
    result = baseline()
    result["run_id"] = "fresh"
    result["components"]["learner"]["kwargs"]["actor_learning_rate"] = 0.0009
    result["metadata"]["qualification"] = "PREPARED_NOT_LAUNCHED; driving unverified; full BLOCKED"
    return result


def test_only_declared_actor_lr_allowed() -> None:
    validate_scope(baseline(), candidate())


@pytest.mark.parametrize("field", ["reward", "training", "entropy", "lr", "identity", "full"])
def test_other_changes_rejected(field: str) -> None:
    value = copy.deepcopy(candidate())
    if field in ("reward", "training"):
        value[field] = {"changed": True}
    elif field == "entropy":
        value["components"]["learner"]["kwargs"]["entropy_coefficient_min"] = 0.001
    elif field == "lr":
        value["components"]["learner"]["kwargs"]["actor_learning_rate"] = 0.0003
    elif field == "identity":
        value["run_id"] = "previous"
    else:
        value["metadata"]["automatic_full_training"] = True
    with pytest.raises(ValueError, match=r"Fresh identity|required|Only actor LR|Full training"):
        validate_scope(baseline(), value)


def test_bounded_window_does_not_allow_stale_launch() -> None:
    plan = {"not_before": NOT_BEFORE, "latest_start": LATEST_START}
    check_start_window(plan, datetime.fromisoformat(NOT_BEFORE))
    with pytest.raises(RuntimeError):
        check_start_window(plan, datetime.fromisoformat("2026-10-08T02:46:00+00:00"))
