"""Paired lidar and image observations with independent sensor branches."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import torch
from gymnasium import spaces
from torch import nn

from trackmaniarl.builtins.features import GymnasiumObservationCollator
from trackmaniarl.core.data import Transition
from trackmaniarl.trackmania.encoders import LidarSensorConfig, LidarSensorEncoder
from trackmaniarl.trackmania.features import LidarFeaturePipeline
from trackmaniarl.trackmania.lidar_feature_setup import LidarFeatureConfig
from trackmaniarl.trackmania.vision import VisionConfig, VisionFeaturePipeline
from trackmaniarl.trackmania.vision_models import VisionSensorEncoder


class LidarVisionFeaturePipeline:
    """Transform paired raw telemetry/RGB without discarding either sensor."""

    def __init__(
        self,
        lidar: LidarFeatureConfig | Mapping[str, Any],
        vision: VisionConfig | Mapping[str, Any] | None = None,
        base_dir: str | Path = ".",
    ) -> None:
        self.lidar = LidarFeaturePipeline(lidar, base_dir=base_dir)
        if self.lidar.history_length != 1:
            raise ValueError("paired lidar uses history_length=1, use a temporal model for history")
        self.vision = VisionFeaturePipeline(vision)
        self.observation_space = spaces.Dict(
            {"lidar": self.lidar.observation_space, "images": self.vision.observation_space}
        )
        self._collator = GymnasiumObservationCollator(self.observation_space)

    def reset_episode(self) -> None:
        self.lidar.reset_episode()
        self.vision.reset_episode()

    def set_evaluation_map(self, map_spec: Any) -> None:
        self.lidar.set_evaluation_map(map_spec)
        self.vision.reset_episode()

    def transform_observation(self, observation: Any) -> dict[str, Any]:
        if not isinstance(observation, Mapping) or set(observation) != {"telemetry", "images"}:
            raise ValueError("paired observations require telemetry and images")
        return {
            "lidar": self.lidar.transform_observation(observation["telemetry"]),
            "images": self.vision.transform_observation(observation["images"]),
        }

    def synthetic_observation(self) -> dict[str, Any]:
        return {
            "telemetry": self.lidar.synthetic_observation(),
            "images": self.vision.synthetic_observation(),
        }

    def collate(self, transitions: list[Transition]) -> dict[str, Any]:
        return dict(self._collator.collate_transitions(transitions))


class BatchedLidarSensorEncoder(nn.Module):
    """Use the frame lidar encoder with batch and optional sequence axes."""

    def __init__(self, config: LidarSensorConfig | Mapping[str, Any]) -> None:
        super().__init__()
        self.sensor = LidarSensorEncoder(config)
        self.output_dim = self.sensor.output_dim

    def forward(self, frames: Mapping[str, torch.Tensor]) -> torch.Tensor:
        if set(frames) != {"lidar", "lidar_mask", "telemetry"}:
            raise ValueError("lidar frames require lidar, lidar_mask, and telemetry tensors")
        leading = frames["telemetry"].shape[:-1]
        if not leading:
            raise ValueError("lidar encoder requires a batch axis")
        ranks = {"lidar": 2, "lidar_mask": 1, "telemetry": 1}
        flat = {}
        for name, value in frames.items():
            rank = ranks[name]
            if value.shape[:-rank] != leading:
                raise ValueError("lidar tensors must share batch and time axes")
            flat[name] = value.reshape(-1, *value.shape[-rank:])
        return cast(torch.Tensor, self.sensor(flat).reshape(*leading, self.output_dim))


class LidarVisionSensorEncoder(nn.Module):
    """Fuse lidar and CNN features while preserving leading batch/time axes."""

    def __init__(
        self,
        lidar: LidarSensorConfig | Mapping[str, Any],
        channels: int = 4,
        output_dim: int = 256,
    ) -> None:
        super().__init__()
        if output_dim < 1:
            raise ValueError("fusion output_dim must be positive")
        self.lidar = BatchedLidarSensorEncoder(lidar)
        self.vision = VisionSensorEncoder(channels, output_dim)
        self.output_dim = output_dim
        self.fusion = nn.Sequential(
            nn.Linear(self.lidar.output_dim + output_dim, output_dim), nn.SiLU()
        )

    def forward(self, frames: Mapping[str, Any]) -> torch.Tensor:
        if set(frames) != {"lidar", "images"}:
            raise ValueError("fusion frames require lidar and images")
        lidar = self.lidar(frames["lidar"])
        images = self.vision(frames["images"])
        if lidar.shape[:-1] != images.shape[:-1]:
            raise ValueError("lidar and images must share batch and time axes")
        return cast(torch.Tensor, self.fusion(torch.cat((lidar, images), dim=-1)))
