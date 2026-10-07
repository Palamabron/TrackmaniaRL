"""Protect episode exclusion, objective weights and the real terminal boundary."""

import numpy as np
import pytest
import torch

from experiments.tmrl_test_comparison.probe_sd_sac_critic import (
    class_weights,
    materialize,
    split_episodes,
)
from trackmaniarl.core.data import Transition
from trackmaniarl.core.replay import InMemoryReplayStore


def test_split_excludes_whole_episodes_reproducibly() -> None:
    codes = np.repeat(np.arange(10), np.arange(1, 11))
    train, held = split_episodes(codes, seed=17421)
    assert not set(codes[train]) & set(codes[held])
    assert set(train) | set(held) == set(range(len(codes)))
    assert np.array_equal(held, split_episodes(codes, seed=17421)[1])


def test_corrected_stratification_preserves_expected_loss_and_gradient() -> None:
    p, q = 0.001, 0.125
    weights = class_weights(np.array([True, False]), p, q)
    value = torch.tensor([3.0, 0.2], requires_grad=True)
    losses = (value - torch.tensor([-2.0, 0.3])).square()
    weighted = (torch.tensor([q, 1 - q]) * torch.tensor(weights) * losses).sum()
    uniform = (torch.tensor([p, 1 - p]) * losses).sum()
    assert float(weighted.detach()) == pytest.approx(float(uniform.detach()))
    assert torch.allclose(
        torch.autograd.grad(weighted, value, retain_graph=True)[0],
        torch.autograd.grad(uniform, value)[0],
    )


@pytest.mark.parametrize(("p", "q"), [(0, 0.1), (0.1, 1), (-0.1, 0.1)])
def test_invalid_probabilities_fail_closed(p: float, q: float) -> None:
    with pytest.raises(ValueError, match="strictly between"):
        class_weights(np.array([True]), p, q)


def test_materialization_preserves_terminal_override_and_no_bootstrap() -> None:
    store = InMemoryReplayStore(capacity=100)
    for step in range(2):
        store.append(
            Transition(
                observation=torch.tensor([float(step)]),
                action=0,
                reward=-2.0 if step else 0.1,
                next_observation=torch.tensor([float(step + 1)]),
                terminated=step == 1,
                truncated=False,
                episode_id="test",
                step=step,
            )
        )
    batch = materialize(dict(store.state_dict()), np.array([0, 1]), 0.995)
    assert torch.equal(batch.next_observations, torch.tensor([[1.0], [2.0]]))
    assert torch.equal(batch.discounts, torch.tensor([0.995, 0.0]))
    assert torch.equal(batch.rewards, torch.tensor([0.1, -2.0]))
