"""Camera BC components using the shared supervised learner and policy lifecycle."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import torch
from gymnasium import spaces
from pydantic import BaseModel, ConfigDict, Field
from torch import nn

from trackmaniarl.builtins.features import GymnasiumObservationCollator
from trackmaniarl.core.contracts import ModelContract
from trackmaniarl.core.data import Transition
from trackmaniarl.trackmania.actions import select_brake_tap_actions
from trackmaniarl.trackmania.imitation_learning.model_contract import BehaviorCloningModel
from trackmaniarl.trackmania.multimodal import LidarVisionFeaturePipeline, LidarVisionSensorEncoder
from trackmaniarl.trackmania.vision import VisionConfig, VisionFeaturePipeline
from trackmaniarl.trackmania.vision_models import VisionSensorEncoder


class VisionBehaviorCloningPipeline:
    """Expose image stacks in the BC mapping observation contract."""

    expects_telemetry = False

    def __init__(self, config: VisionConfig | Mapping[str, Any] | None = None) -> None:
        self.images = VisionFeaturePipeline(config)
        self.config = self.images.config
        self.observation_space = spaces.Dict({"images": self.images.observation_space})
        self._collator = GymnasiumObservationCollator(self.observation_space)

    def reset_episode(self) -> None:
        self.images.reset_episode()

    def transform_observation(self, observation: Any) -> dict[str, torch.Tensor]:
        return {"images": self.images.transform_observation(observation)}

    def synthetic_observation(self) -> Any:
        return self.images.synthetic_observation()

    def collate(self, transitions: list[Transition]) -> dict[str, Any]:
        return dict(self._collator.collate_transitions(transitions))


class VisionBehaviorCloningConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    channels: int = Field(default=4, ge=1)
    lidar: dict[str, Any] | None = None
    hidden_dim: int = Field(default=256, ge=1)
    previous_action_conditioning: bool = False
    switch_logit_margin: float = Field(default=0.0, ge=0.0, allow_inf_nan=False)


class VisionBehaviorCloningModel(BehaviorCloningModel):
    def __init__(
        self,
        action_ids: tuple[int, ...],
        config: VisionBehaviorCloningConfig,
        minimum_action_hold_steps: int = 1,
    ) -> None:
        super().__init__()
        select_brake_tap_actions(action_ids)
        self.action_ids = tuple(action_ids)
        self.action_count = len(self.action_ids)
        self.previous_action_start = self.action_count
        self.previous_action_conditioning = config.previous_action_conditioning
        if minimum_action_hold_steps < 1:
            raise ValueError("minimum_action_hold_steps must be positive")
        self.minimum_action_hold_steps = minimum_action_hold_steps
        self.switch_logit_margin = config.switch_logit_margin
        self.paired = config.lidar is not None
        self.encoder = (
            VisionSensorEncoder(config.channels, config.hidden_dim)
            if config.lidar is None
            else LidarVisionSensorEncoder(config.lidar, config.channels, config.hidden_dim)
        )
        self.previous_action_embedding = (
            nn.Embedding(self.action_count + 1, config.hidden_dim)
            if config.previous_action_conditioning
            else None
        )
        self.head = nn.Linear(config.hidden_dim, self.action_count)

    def initial_policy_state(self, device: torch.device) -> None:
        return None

    def policy_logits(
        self, observation: Mapping[str, torch.Tensor], state: Any
    ) -> tuple[torch.Tensor, None]:
        return self(observation), None

    def forward(self, observation: Mapping[str, torch.Tensor]) -> torch.Tensor:
        images = observation["images"]
        if images.ndim != 4:
            raise ValueError("BC images must have shape (batch, channels, height, width)")
        features = self.encoder(
            {
                "images": images,
                "lidar": {key: observation[key] for key in ("lidar", "lidar_mask", "telemetry")},
            }
            if self.paired
            else images
        )
        if self.previous_action_embedding is not None:
            if "previous_action" not in observation:
                raise ValueError("previous_action is required by this behavior-cloning model")
            features = features + self.previous_action_embedding(
                observation["previous_action"].long()
            )
        return cast(torch.Tensor, self.head(features))


class VisionBehaviorCloningModelFactory:
    model_contract = ModelContract.CATEGORICAL_POLICY

    def __init__(
        self,
        action_ids: tuple[int, ...],
        config: VisionBehaviorCloningConfig | Mapping[str, Any] | None = None,
        minimum_action_hold_steps: int = 1,
    ) -> None:
        select_brake_tap_actions(tuple(action_ids))
        self.action_ids = tuple(action_ids)
        self.config = VisionBehaviorCloningConfig.model_validate({} if config is None else config)
        self.minimum_action_hold_steps = minimum_action_hold_steps

    def build(self) -> VisionBehaviorCloningModel:
        return VisionBehaviorCloningModel(
            self.action_ids, self.config, self.minimum_action_hold_steps
        )


class LidarVisionBehaviorCloningPipeline(VisionBehaviorCloningPipeline):
    """Flatten paired sensor fields for the shared BC dataset and policy contract."""

    expects_telemetry = True

    def __init__(
        self,
        lidar: Mapping[str, Any],
        vision: VisionConfig | Mapping[str, Any] | None = None,
        base_dir: str | Path = ".",
    ) -> None:
        self.paired = LidarVisionFeaturePipeline(lidar, vision, base_dir)
        self.images = self.paired.vision
        self.config = self.images.config
        sensor = self.paired.lidar
        if sensor.include_control_inputs and not sensor.mask_current_control_inputs:
            raise ValueError("paired BC requires masked current controls to prevent target leakage")
        self.local_velocity_features = sensor.local_velocity_features
        self.observation_space = spaces.Dict(
            {**sensor.observation_space.spaces, "images": self.images.observation_space}
        )
        self._collator = GymnasiumObservationCollator(self.observation_space)

    def reset_episode(self) -> None:
        self.paired.reset_episode()

    def set_evaluation_map(self, map_spec: Any) -> None:
        self.paired.set_evaluation_map(map_spec)

    def transform_observation(self, observation: Any) -> dict[str, torch.Tensor]:
        prepared = self.paired.transform_observation(observation)
        return {**prepared["lidar"], "images": prepared["images"]}

    def synthetic_observation(self) -> Any:
        return self.paired.synthetic_observation()
