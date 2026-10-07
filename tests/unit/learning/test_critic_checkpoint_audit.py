from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from experiments.tmrl_test_comparison.audit_sd_sac_critic import recorded_returns


def replay_fixture() -> dict[str, Any]:
    return {
        "size": 4,
        "next_index": 14,
        "rewards": np.array([1.0, 2.0, -3.0, 9.0]),
        "terminated": np.array([False, False, True, False]),
        "truncated": np.array([False, False, False, False]),
        "next_ids": np.array([11, 12, -1, -1]),
        "episode_codes": np.array([0, 0, 0, 1]),
        "steps": np.array([0, 1, 2, 0]),
        "info": {
            10: {"_trackmaniarl_behavior_entropy": 100.0},
            11: {"_trackmaniarl_behavior_entropy": 2.0},
            12: {"_trackmaniarl_behavior_entropy": 4.0},
        },
    }


def test_recorded_soft_returns_include_future_entropy_and_no_terminal_bootstrap() -> None:
    values = recorded_returns(replay_fixture(), gamma=0.5, alpha=0.1)
    # Terminal Q is exactly the reward. Current-state entropy (100) is excluded.
    np.testing.assert_allclose(values[:3], [[1.25, 1.45, 3], [0.5, 0.7, 2], [-3, -3, 1]])
    assert np.isnan(values[3]).all()  # Live tail has no invented continuation.


@pytest.mark.parametrize("field", ["truncated", "episode_codes", "steps", "next_ids", "info"])
def test_recorded_returns_reject_truncations_and_broken_suffixes(field: str) -> None:
    replay = replay_fixture()
    if field == "truncated":
        replay[field][2] = True
    elif field == "episode_codes":
        replay[field][2] = 2
    elif field == "steps":
        replay[field][2] = 7
    elif field == "next_ids":
        replay[field][1] = 10  # Cycle/backward link.
    else:
        del replay[field][12]["_trackmaniarl_behavior_entropy"]
    values = recorded_returns(replay, gamma=0.5, alpha=0.1)
    assert np.isnan(values[:2]).all()
