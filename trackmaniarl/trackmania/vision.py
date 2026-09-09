"""RGB camera observations, preprocessing and episode-local frame stacking."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from typing import Any

import numpy as np
import torch
from gymnasium import spaces
from pydantic import BaseModel, ConfigDict, Field
from torch.nn import functional as F

from trackmaniarl.builtins.features import GymnasiumObservationCollator
from trackmaniarl.core.data import Transition


class VisionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    width: int = Field(default=84, ge=8)
    height: int = Field(default=84, ge=8)
    grayscale: bool = True
    frame_stack: int = Field(default=4, ge=1)

    @property
    def channels(self) -> int:
        return self.frame_stack * (1 if self.grayscale else 3)


class VisionFeaturePipeline:
    """Convert uint8 HWC RGB to stacked float32 CHW images in [0, 1].

    Replay stores the transformed stack. Collation never advances camera history.
    The first frame is repeated on reset, so stacks cannot leak across episodes.
    """

    def __init__(self, config: VisionConfig | Mapping[str, Any] | None = None) -> None:
        self.config = VisionConfig.model_validate({} if config is None else config)
        self._frames: deque[torch.Tensor] = deque(maxlen=self.config.frame_stack)
        shape = (self.config.channels, self.config.height, self.config.width)
        self.observation_space = spaces.Box(0.0, 1.0, shape=shape, dtype=np.float32)
        self._collator = GymnasiumObservationCollator(self.observation_space)

    def reset_episode(self) -> None:
        self._frames.clear()

    def transform_observation(self, observation: Any) -> torch.Tensor:
        frame = torch.as_tensor(np.ascontiguousarray(observation))
        if frame.dtype != torch.uint8 or frame.ndim != 3 or frame.shape[-1] != 3:
            raise ValueError("camera observation must be uint8 RGB with shape (height, width, 3)")
        if min(frame.shape[:2]) < 1:
            raise ValueError("camera frame must not be empty")
        frame = frame.permute(2, 0, 1).float().div_(255.0)
        if self.config.grayscale:
            weights = frame.new_tensor([0.299, 0.587, 0.114])[:, None, None]
            frame = (frame * weights).sum(dim=0, keepdim=True)
        frame = F.interpolate(
            frame.unsqueeze(0),
            size=(self.config.height, self.config.width),
            mode="bilinear",
            align_corners=False,
            antialias=True,
        )[0].clamp_(0.0, 1.0)
        if not self._frames:
            self._frames.extend([frame] * self.config.frame_stack)
        else:
            self._frames.append(frame)
        return torch.cat(tuple(self._frames), dim=0)

    def collate(self, transitions: list[Transition]) -> dict[str, Any]:
        return dict(self._collator.collate_transitions(transitions))

    def synthetic_observation(self) -> np.ndarray[Any, Any]:
        return np.zeros((self.config.height, self.config.width, 3), dtype=np.uint8)
