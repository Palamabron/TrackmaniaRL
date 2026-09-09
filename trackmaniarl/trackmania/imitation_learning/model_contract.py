"""Observation-independent model contract shared by BC training and policies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

import torch
from torch import nn


class BehaviorCloningModel(nn.Module, ABC):
    action_ids: tuple[int, ...]
    action_count: int
    previous_action_conditioning: bool
    previous_action_start: int
    minimum_action_hold_steps: int
    switch_logit_margin: float

    @abstractmethod
    def initial_policy_state(self, device: torch.device) -> Any:
        raise NotImplementedError

    @abstractmethod
    def policy_logits(
        self, observation: Mapping[str, torch.Tensor], state: Any
    ) -> tuple[torch.Tensor, Any]:
        raise NotImplementedError

    @abstractmethod
    def forward(self, observation: Mapping[str, torch.Tensor]) -> torch.Tensor:
        raise NotImplementedError
