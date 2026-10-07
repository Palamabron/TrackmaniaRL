"""Diagnostic ranks, class normalization and paired uncertainty must be explicit."""

import numpy as np
import pytest
import torch

from experiments.tmrl_test_comparison.probe_sd_sac_joint_calibration import (
    joint_loss,
    landscape,
    paired_interval,
    tree_digest,
)


def test_landscape_distinguishes_range_rank_regret_and_ties() -> None:
    values = np.array([[1, 3, 2], [3, 1, 2], [2, 2, 2]], dtype=float)
    result = landscape(values, 0)
    assert result["margin_max_minus_min"]["mean"] == pytest.approx(4 / 3)
    assert result["per_state"]["chosen_rank"] == [3, 1, 1]
    assert result["per_state"]["chosen_percentile"] == [0, 100, 50]
    assert result["regret_best_minus_chosen"]["mean"] == pytest.approx(2 / 3)
    assert result["chosen_tied_for_best_fraction"] == pytest.approx(2 / 3)


def test_joint_weight_is_not_diluted_by_terminal_batch_size() -> None:
    nonterminal = torch.tensor([[1.0], [2.0]], requires_grad=True)
    terminal = torch.tensor([[3.0], [4.0]], requires_grad=True)
    loss = joint_loss(nonterminal, terminal, 0.1)
    repeated = joint_loss(nonterminal.repeat(1, 30), terminal.repeat(1, 2), 0.1)
    assert float(loss.detach()) == pytest.approx(7.5)
    assert torch.allclose(loss, repeated)
    terminal_gradient = torch.autograd.grad(loss, terminal)[0]
    assert torch.allclose(terminal_gradient, torch.tensor([[0.6], [0.8]]))


def test_paired_bootstrap_detects_consistent_reduction_without_inflating_episodes() -> None:
    result = paired_interval(np.ones((2, 27)))
    assert result["family_adjusted_interval"] == [1.0, 1.0]
    assert result["positive_lower_bound"]
    assert result["episodes"] == 27
    assert not paired_interval(np.zeros((2, 27)))["positive_lower_bound"]


def test_saved_adam_digest_detects_mutation_and_accepts_independent_copy() -> None:
    state = {"moment": torch.tensor([1.0, 2.0]), "step": 4}
    copied = {"moment": state["moment"].clone(), "step": 4}
    assert tree_digest(state) == tree_digest(copied)
    copied["moment"][0] = 3
    assert tree_digest(state) != tree_digest(copied)
