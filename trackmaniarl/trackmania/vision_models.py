"""First-party CNN actor-value model for image-based Trackmania PPO."""

from __future__ import annotations

import torch
from torch import nn

from trackmaniarl.core.contracts import ModelContract
from trackmaniarl.models.actors import GaussianActorConfig, PpoGaussianActor
from trackmaniarl.models.critics import ContinuousValueCritic
from trackmaniarl.models.encoders.convolutional import ConvolutionalSensorEncoder


class VisionSensorEncoder(ConvolutionalSensorEncoder):
    """Encode normalized CHW stacks, preserving any leading batch/time axes."""

    def __init__(self, channels: int = 4, output_dim: int = 256, hidden_dim: int = 64) -> None:
        super().__init__(channels, output_dim, hidden_dim)

    def forward(self, frames: torch.Tensor) -> torch.Tensor:
        if frames.ndim < 4 or frames.shape[-3] != self.channels:
            raise ValueError("vision input must have shape (..., channels, height, width)")
        leading = frames.shape[:-3]
        features = super().forward(frames.reshape(-1, *frames.shape[-3:]))
        return features.reshape(*leading, self.output_dim)


class VisionPpoModel(nn.Module):
    def __init__(self, channels: int = 4, hidden_dim: int = 256) -> None:
        super().__init__()
        self.actor = PpoGaussianActor(
            VisionSensorEncoder(channels, hidden_dim),
            GaussianActorConfig(
                hidden_dim, 3, action_low=(0.0, 0.0, -1.0), action_high=(1.0, 1.0, 1.0)
            ),
        )
        self.value = ContinuousValueCritic(VisionSensorEncoder(channels, hidden_dim), hidden_dim)


class VisionPpoModelFactory:
    model_contract = ModelContract.CONTINUOUS_ACTOR_VALUE

    def __init__(self, channels: int = 4, hidden_dim: int = 256) -> None:
        if channels < 1 or hidden_dim < 1:
            raise ValueError("vision model dimensions must be positive")
        self.channels, self.hidden_dim = channels, hidden_dim

    def build(self) -> VisionPpoModel:
        return VisionPpoModel(self.channels, self.hidden_dim)
