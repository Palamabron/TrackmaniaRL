import pytest
import torch

from experiments.tmrl_test_comparison.probe_sd_sac_projected_calibration import (
    LossSettings,
    calibration_loss,
)


def test_zero_extra_loss_restores_empirical_class_prevalence() -> None:
    current = torch.tensor([[1.0, 3.0], [2.0, 4.0]])
    target = torch.zeros(2)
    loss = calibration_loss((current, current, target), LossSettings(0.1, 0, 0.5))
    assert float(loss) == pytest.approx(0.9 * 5 + 0.1 * 25)


def test_explicit_terminal_loss_does_not_reweight_nonterminals() -> None:
    current = torch.tensor([[1.0, 3.0], [2.0, 4.0]])
    target = torch.zeros(2)
    loss = calibration_loss((current, current, target), LossSettings(0.1, 0.2, 0.5))
    assert float(loss) == pytest.approx(7 + 0.2 * 25)


def test_clipped_branch_blocks_baseline_but_extra_terminal_loss_has_gradient() -> None:
    current = torch.ones((2, 2), requires_grad=True)
    old = torch.zeros_like(current)
    target = torch.full((2,), 10.0)
    baseline = calibration_loss((current, old, target), LossSettings(0.1, 0, 0.5))
    baseline.backward()
    assert torch.equal(current.grad, torch.zeros_like(current))
    current.grad = None
    extra = calibration_loss((current, old, target), LossSettings(0.1, 0.2, 0.5))
    extra.backward()
    assert torch.equal(current.grad[:, 0], torch.zeros(2))
    assert torch.allclose(current.grad[:, 1], torch.full((2,), -3.6))
