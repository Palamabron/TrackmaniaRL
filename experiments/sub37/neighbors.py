"""State-conditioned action support from complete online reference episodes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import torch

from experiments.sub37.policy import (
    Sub37Policy,
    reference_episodes,
    replay_columns,
)
from trackmaniarl.core.contracts import PolicyMode


def reference_features(observation: Mapping[str, Any]) -> torch.Tensor:
    physics = torch.as_tensor(observation["physics"])
    context = torch.as_tensor(observation["context"])
    values = torch.cat((physics[..., [3, 0, 1, 2, 4, 6, 7]], context[..., [0, 4, 5]]), dim=-1)
    scales = values.new_tensor([400, 10, 10, 2, 3, 3, 3, 4, 1, 3])
    return values * scales


def reference_bank(replay: Mapping[str, Any]) -> tuple[torch.Tensor, torch.Tensor]:
    rows = np.concatenate(reference_episodes(replay))
    columns = replay_columns(replay)
    rows = rows[(columns["physics"][rows, 3] >= 0.54) & (columns["physics"][rows, 3] < 0.90)]
    observations = {key: value[rows] for key, value in columns.items()}
    actions = np.asarray(replay["actions"]["arrays"][0][rows]).reshape(-1)
    return reference_features(observations), torch.as_tensor(actions, dtype=torch.long)


def neighbor_mask(
    bank: tuple[torch.Tensor, torch.Tensor], query: torch.Tensor
) -> torch.Tensor | None:
    votes = neighbor_votes(bank, query)
    return None if votes is None else votes > 0


def neighbor_votes(
    bank: tuple[torch.Tensor, torch.Tensor], query: torch.Tensor
) -> torch.Tensor | None:
    features, actions = bank
    distances = (features - query).square().sum(dim=-1)
    nearest = distances.topk(min(15, len(distances)), largest=False)
    # The reference cannot provide evidence for distant/off-trajectory states.
    if nearest.values[0] > 9.0:
        return None
    return torch.bincount(actions[nearest.indices], minlength=78)


class NeighborPolicy(Sub37Policy):
    def configure_references(self, replay: Mapping[str, Any]) -> None:
        features, actions = reference_bank(replay)
        self.bank = (features.to(self.base.device), actions.to(self.base.device))

    def act(self, observation: Any, mode: PolicyMode = PolicyMode.EVALUATION) -> int:
        self.query = reference_features(observation).to(self.base.device)
        self.speed = float(observation["physics"][0])
        return super().act(observation, mode)

    def _values(self, features: torch.Tensor, progress: float) -> torch.Tensor:
        values = super()._values(features, progress)
        start = 0.63 if self.experiment.drive_exit else 0.54
        if not start <= progress < 0.90 or self.speed < 0.15:
            return values
        votes = neighbor_votes(self.bank, self.query)
        if votes is None:
            self._record_choice(progress, values, values)
            return values
        allowed = votes == votes.max() if self.experiment.neighbor_vote else votes > 0
        masked = values.masked_fill(~allowed, -torch.inf)
        if not torch.isfinite(masked).any():
            return values
        changes = self.current.get("neighbor_changes", 0)
        self.current["neighbor_changes"] = changes + int(masked.argmax() != values.argmax())
        self._record_choice(progress, values, masked)
        return masked

    def _record_choice(
        self, progress: float, original: torch.Tensor, selected: torch.Tensor
    ) -> None:
        rows = self.current.setdefault("neighbor_trace", [])
        rows.append(
            [
                progress,
                *self.query.detach().cpu().tolist(),
                int(original.argmax()),
                int(selected.argmax()),
            ]
        )
