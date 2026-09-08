"""Regression checks for experimental lower-tail integration and action envelopes."""

from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest
import torch

from experiments.sub37.policy import (
    EXPERIMENTS,
    Sub37Policy,
    build_envelope,
    reference_episodes,
)
from trackmaniarl.models.contracts import RiskSpec, ValueSupport

pytestmark = pytest.mark.must_have


class _QuantileModel:
    action_count = 78

    def expected_all_actions(
        self, features: torch.Tensor, support: ValueSupport, risk: RiskSpec
    ) -> torch.Tensor:
        del features, risk
        # A risky action dominates only in the upper half; safe action is constant.
        risky = (support.points >= 0.5).float() * 10.0
        output = torch.zeros(1, 78)
        output[0, 0] = (risky * support.weights).sum()
        output[0, 1] = 3.0
        return output


def _policy(name: str) -> Sub37Policy:
    base = SimpleNamespace(
        model=_QuantileModel(),
        device=torch.device("cpu"),
        action_selector=None,
        _mask=lambda values: values,
    )
    policy = Sub37Policy(base, EXPERIMENTS[name], torch.ones(200, 78, dtype=torch.bool))
    policy.current = {"envelope_changes": 0, "changed": 0}
    return policy


def test_lower_tail_prefers_safe_action_without_sorting_actions() -> None:
    policy = _policy("cvar50")
    features = torch.zeros(1, 4)
    assert policy._integrate(features, 1.0).argmax().item() == 0
    assert policy._integrate(features, 0.5).argmax().item() == 1


def test_envelope_chooses_highest_q_allowed_and_respects_window() -> None:
    policy = _policy("envelope")
    policy.envelope[:] = False
    policy.envelope[:, [69, 75]] = True
    values = torch.zeros(1, 78)
    values[0, 59], values[0, 69], values[0, 75] = 10, 8, 7
    assert policy._enforce_envelope(values, 0.58).argmax().item() == 69
    assert policy._enforce_envelope(values, 0.90).argmax().item() == 59
    policy.envelope[:] = False
    torch.testing.assert_close(policy._enforce_envelope(values, 0.58), values)


def test_drive_exit_is_local_and_preserves_recovery_after_middle_corner() -> None:
    policy = _policy("envelope-drive")
    values = torch.zeros(1, 78)
    values[0, 72] = 10
    policy.base._q_values = lambda features, mode: values
    features = torch.zeros(1, 4)
    assert policy._values(features, 0.568).argmax().item() == 75
    assert policy._values(features, 0.590).argmax().item() == 72
    assert policy._values(features, 0.80).argmax().item() == 72


def _replay() -> dict[str, Any]:
    size = 5 * 720
    physics = np.zeros((size, 60), dtype=np.float32)
    physics[:, 3] = np.tile(np.linspace(0, 0.999, 720), 5)
    terminated = np.zeros(size, dtype=bool)
    terminated[719::720] = True
    return {
        "observations": {"spec": ("mapping", ("physics",), (("leaf", 0),)), "arrays": [physics]},
        "actions": {"arrays": [np.full(size, 75, dtype=np.int64)]},
        "episode_codes": np.repeat(np.arange(5), 720),
        "episode_names": {code: f"online-{code}" for code in range(5)},
        "steps": np.tile(np.arange(720), 5),
        "terminated": terminated,
        "truncated": np.zeros(size, dtype=bool),
    }


def test_reference_filter_excludes_demos_partial_and_truncated_laps() -> None:
    replay = _replay()
    assert len(reference_episodes(replay)) == 5
    assert build_envelope(replay)[:, 75].all()
    replay["episode_names"][0] = "demo-human"
    replay["truncated"][1439] = True
    replay["steps"][1440] = 9
    assert len(reference_episodes(replay)) == 2
    with pytest.raises(ValueError, match="at least five"):
        build_envelope(replay)
