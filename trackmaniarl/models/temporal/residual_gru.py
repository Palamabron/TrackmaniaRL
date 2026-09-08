"""Policy-preserving residual GRU temporal core."""

from __future__ import annotations

from math import isfinite

import torch
from torch import nn

from trackmaniarl.core.pytree import PyTree


def _validate_config(input_dim: int, hidden_dim: int, residual_scale: float) -> None:
    if input_dim < 1 or hidden_dim < 1:
        raise ValueError("residual GRU dimensions must be positive")
    if not isfinite(residual_scale) or not 0.0 < residual_scale <= 1.0:
        raise ValueError("residual_scale must be finite and in (0, 1]")


class ZeroGatedResidualGruTemporalCore(nn.Module):
    """Add bounded recurrent context while exactly preserving a frame policy.

    The learnable gate starts at zero, so replacing an identity temporal core
    does not change a warm-started policy.  The recurrent correction is bounded
    per feature to keep the adaptation deliberately conservative.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int | None = None,
        residual_scale: float = 0.02,
    ) -> None:
        super().__init__()
        hidden_dim = input_dim if hidden_dim is None else hidden_dim
        _validate_config(input_dim, hidden_dim, residual_scale)
        self.input_dim = input_dim
        self.output_dim = input_dim
        self.hidden_dim = hidden_dim
        self.residual_scale = float(residual_scale)
        self.recurrent = nn.GRU(input_dim, hidden_dim, batch_first=True)
        self.normalization = nn.LayerNorm(hidden_dim)
        self.projection = nn.Linear(hidden_dim, input_dim)
        self.residual_gate = nn.Parameter(torch.zeros(input_dim))

    def unroll(self, features: torch.Tensor, burn_in: int) -> torch.Tensor:
        self._validate(features, burn_in)
        hidden: torch.Tensor | None = None
        if burn_in:
            with torch.no_grad():
                _, hidden = self.recurrent(features[:, :burn_in])
            hidden = hidden.detach()
        suffix = features[:, burn_in:]
        values, _ = self.recurrent(suffix, hidden)
        return self._residual(suffix, values)

    def initial_state(self, batch_size: int, device: torch.device) -> PyTree:
        return torch.zeros(1, batch_size, self.hidden_dim, device=device)

    def step(self, feature: torch.Tensor, state: PyTree) -> tuple[torch.Tensor, PyTree]:
        if not isinstance(state, torch.Tensor):
            raise TypeError("residual GRU state must be a tensor")
        if feature.ndim != 2 or feature.shape[-1] != self.input_dim:
            raise ValueError("residual GRU step feature must have shape (batch, input_dim)")
        values, hidden = self.recurrent(feature.unsqueeze(1), state)
        output = self._residual(feature.unsqueeze(1), values)[:, 0]
        return output, hidden

    def _residual(self, features: torch.Tensor, recurrent: torch.Tensor) -> torch.Tensor:
        correction = torch.tanh(self.projection(self.normalization(recurrent)))
        gate = torch.tanh(self.residual_gate).view(1, 1, -1)
        return features + self.residual_scale * gate * correction

    def _validate(self, features: torch.Tensor, burn_in: int) -> None:
        if features.ndim != 3 or features.shape[-1] != self.input_dim:
            raise ValueError("residual GRU features must have shape (batch, time, input_dim)")
        if not 0 <= burn_in < features.shape[1]:
            raise ValueError("burn_in must be in [0, time)")
