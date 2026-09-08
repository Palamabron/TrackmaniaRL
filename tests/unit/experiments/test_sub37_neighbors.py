"""Neighbor support must distinguish state, not just track progress."""

from types import SimpleNamespace

import pytest
import torch

from experiments.sub37.neighbors import (
    NeighborPolicy,
    neighbor_mask,
    reference_features,
)
from experiments.sub37.policy import EXPERIMENTS

pytestmark = pytest.mark.must_have


def test_same_progress_opposite_lateral_offsets_select_different_support() -> None:
    physics = torch.zeros(32, 60)
    physics[:, 3] = 0.80
    context = torch.zeros(32, 29)
    context[:16, 0] = -0.8
    context[16:, 0] = 0.8
    features = reference_features({"physics": physics, "context": context})
    actions = torch.tensor([21] * 16 + [75] * 16)
    left = neighbor_mask((features, actions), features[0])
    right = neighbor_mask((features, actions), features[-1])
    assert left is not None
    assert right is not None
    assert left[21]
    assert not left[75]
    assert right[75]
    assert not right[21]


def test_distant_state_does_not_restrict_recovery() -> None:
    bank = (torch.zeros(20, 10), torch.zeros(20, dtype=torch.long))
    assert neighbor_mask(bank, torch.ones(10) * 10) is None


def _neighbor_policy(name: str = "neighbors") -> NeighborPolicy:
    values = torch.zeros(1, 78)
    values[0, 59], values[0, 69], values[0, 75] = 10, 8, 7
    base = SimpleNamespace(
        model=SimpleNamespace(action_count=78),
        device=torch.device("cpu"),
        action_selector=None,
        _q_values=lambda features, mode: values,
    )
    policy = NeighborPolicy(base, EXPERIMENTS[name], torch.ones(200, 78, dtype=torch.bool))
    policy.current = {"changed": 0, "envelope_changes": 0}
    policy.bank = (torch.zeros(15, 10), torch.tensor([69] * 5 + [75] * 10))
    policy.query = torch.zeros(10)
    policy.speed = 0.6
    return policy


def test_neighbors_uses_q_not_majority_and_counts_interventions() -> None:
    policy = _neighbor_policy()
    assert policy._values(torch.zeros(1, 4), 0.60).argmax().item() == 69
    assert policy.current["neighbor_changes"] == 1
    assert policy.current["neighbor_trace"][0][-2:] == [59, 69]


def test_vote_variant_selects_most_frequent_reference_action() -> None:
    policy = _neighbor_policy("neighbors-vote")
    assert policy._values(torch.zeros(1, 4), 0.60).argmax().item() == 75


@pytest.mark.parametrize(("progress", "speed"), [(0.539, 0.6), (0.9, 0.6), (0.6, 0.149)])
def test_outside_window_or_slow_recovery_keeps_source(progress: float, speed: float) -> None:
    policy = _neighbor_policy()
    policy.speed = speed
    assert policy._values(torch.zeros(1, 4), progress).argmax().item() == 59


def test_global_action_mask_is_not_overridden_by_neighbors() -> None:
    policy = _neighbor_policy()
    values = policy.base._q_values(None, None)
    values[0, [69, 75]] = -torch.inf
    assert policy._values(torch.zeros(1, 4), 0.6).argmax().item() == 59
