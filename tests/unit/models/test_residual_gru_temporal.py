from __future__ import annotations

import pytest
import torch

from trackmaniarl.models.temporal import ZeroGatedResidualGruTemporalCore


def test_residual_gru_is_exact_identity_at_initialization() -> None:
    torch.manual_seed(4)
    core = ZeroGatedResidualGruTemporalCore(12, hidden_dim=7, residual_scale=0.03)
    features = torch.randn(3, 6, 12)

    output = core.unroll(features, burn_in=2)
    step, state = core.step(features[:, 0], core.initial_state(3, features.device))

    torch.testing.assert_close(output, features[:, 2:], rtol=0.0, atol=0.0)
    torch.testing.assert_close(step, features[:, 0], rtol=0.0, atol=0.0)
    assert isinstance(state, torch.Tensor)
    assert state.shape == (1, 3, 7)


def test_residual_gru_gate_learns_and_correction_is_bounded() -> None:
    scale = 0.03
    core = ZeroGatedResidualGruTemporalCore(8, residual_scale=scale)
    features = torch.randn(2, 5, 8)

    core.unroll(features, burn_in=1).sum().backward()
    assert core.residual_gate.grad is not None
    assert torch.count_nonzero(core.residual_gate.grad) > 0

    with torch.no_grad():
        core.residual_gate.fill_(100.0)
    correction = core.unroll(features, burn_in=1) - features[:, 1:]
    assert correction.abs().max() <= scale


@pytest.mark.parametrize("scale", [0.0, -0.1, 1.01, float("inf")])
def test_residual_gru_rejects_invalid_scale(scale: float) -> None:
    with pytest.raises(ValueError, match="residual_scale"):
        ZeroGatedResidualGruTemporalCore(8, residual_scale=scale)
