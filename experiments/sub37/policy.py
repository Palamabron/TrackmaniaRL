"""Opt-in inference experiments for the 78-action, V5 TrackMania policy.

These are hypotheses, not validated replacements for the source policy. The
envelope uses training replay only; benchmark outcomes never update its mask.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch

from trackmaniarl.algorithms.value_based.policy import DiscreteValuePolicy
from trackmaniarl.core.contracts import PolicyMode
from trackmaniarl.models.contracts import RiskSpec, ValueSupport


@dataclass(frozen=True)
class InferenceExperiment:
    name: str
    quantiles: int = 32
    lower_tail: float = 1.0
    envelope: bool = False
    drive_exit: bool = False
    drive_stop: float = 0.590
    neighbor_vote: bool = False
    start: float = 0.54
    stop: float = 0.90


EXPERIMENTS = {
    item.name: item
    for item in (
        InferenceExperiment("baseline"),
        InferenceExperiment("dense", quantiles=128),
        InferenceExperiment("cvar75", quantiles=128, lower_tail=0.75),
        InferenceExperiment("cvar50", quantiles=128, lower_tail=0.50),
        InferenceExperiment("envelope", envelope=True),
        InferenceExperiment("envelope-cvar75", lower_tail=0.75, envelope=True),
        InferenceExperiment("envelope-drive", envelope=True, drive_exit=True, stop=0.62),
        InferenceExperiment(
            "envelope-drive-long", envelope=True, drive_exit=True, drive_stop=0.62, stop=0.63
        ),
        InferenceExperiment(
            "drive-neighbors", envelope=True, drive_exit=True, drive_stop=0.62, stop=0.63
        ),
        InferenceExperiment("neighbors"),
        InferenceExperiment("neighbors-vote", neighbor_vote=True),
    )
}


def replay_columns(replay: Mapping[str, Any]) -> dict[str, Any]:
    snapshot = replay["observations"]
    kind, keys, specs = snapshot["spec"]
    if kind != "mapping" or any(spec[0] != "leaf" for spec in specs):
        raise ValueError("expected a flat V5 observation mapping")
    return {key: snapshot["arrays"][spec[1]] for key, spec in zip(keys, specs, strict=True)}


def reference_episodes(replay: Mapping[str, Any]) -> list[np.ndarray[Any, Any]]:
    """Select complete online laps by step count; this is not a race-time label."""
    physics = replay_columns(replay)["physics"]
    result = []
    for code, name in replay["episode_names"].items():
        if name.startswith("demo-"):
            continue
        rows = np.flatnonzero(replay["episode_codes"] == code)
        rows = rows[np.argsort(replay["steps"][rows])]
        if _reference_complete(replay, rows) and physics[rows[-1], 3] > 0.99:
            result.append(rows)
    return result


def _reference_complete(replay: Mapping[str, Any], rows: np.ndarray[Any, Any]) -> bool:
    return bool(
        700 <= len(rows) <= 750
        and np.array_equal(replay["steps"][rows], np.arange(len(rows)))
        and replay["terminated"][rows[-1]]
        and not replay["truncated"][rows[-1]]
    )


def build_envelope(replay: Mapping[str, Any]) -> torch.Tensor:
    episodes = reference_episodes(replay)
    if len(episodes) < 5:
        raise ValueError("envelope requires at least five complete online reference laps")
    rows = np.concatenate(episodes)
    progress = replay_columns(replay)["physics"][rows, 3]
    actions = np.asarray(replay["actions"]["arrays"][0][rows]).reshape(-1)
    if np.any(actions < 0) or np.any(actions >= 78):
        raise ValueError("envelope requires the original 78-action encoding")
    bins = np.clip((progress * 200).astype(int), 0, 199)
    mask = np.zeros((200, 78), dtype=bool)
    mask[bins, actions] = True
    # Union adjacent 0.5%-bins to tolerate boundaries and line variation.
    widened = mask.copy()
    widened[1:] |= mask[:-1]
    widened[:-1] |= mask[1:]
    return torch.from_numpy(widened)


class Sub37Policy:
    """Closed-loop policy with explicit, logged evaluation-only interventions."""

    def __init__(
        self,
        base: DiscreteValuePolicy,
        experiment: InferenceExperiment,
        envelope: torch.Tensor,
    ) -> None:
        if base.model.action_count != 78:
            raise ValueError("sub37 experiments require 78 actions")
        selector = base.action_selector
        if selector is not None and (
            selector.minimum_action_hold_steps != 1 or selector.switch_q_margin != 0.0
        ):
            raise ValueError("experiments require unheld, zero-margin action selection")
        self.base = base
        self.experiment = experiment
        self.envelope = envelope.to(base.device)
        self.episodes: list[dict[str, Any]] = []
        self.current: dict[str, Any] = {}

    def reset_episode(self) -> None:
        self.base.reset_episode()
        self.current = {"steps": 0, "changed": 0, "envelope_changes": 0, "trace": []}
        self.episodes.append(self.current)

    def act(self, observation: Any, mode: PolicyMode = PolicyMode.EVALUATION) -> int:
        if mode is not PolicyMode.EVALUATION:
            raise ValueError("experimental wrapper supports benchmark evaluation only")
        if not self.current:
            self.reset_episode()
        progress = float(observation["physics"][3])
        with torch.no_grad():
            batched = self.base._prepare_observation(observation)
            features, self.base._state = self.base.model.policy_step(batched, self.base._state)
            values = self._values(features, progress)
            action = self.base._select_action(values, mode)
        self.current["steps"] += 1
        self._trace(observation, int(action.item()))
        return int(action.item())

    def _values(self, features: torch.Tensor, progress: float) -> torch.Tensor:
        original = self.base._q_values(features, PolicyMode.EVALUATION)
        values = original
        spec = self.experiment
        active = spec.start <= progress < spec.stop
        if spec.quantiles != 32 or (active and spec.lower_tail != 1.0):
            alpha = spec.lower_tail if active else 1.0
            values = self._integrate(features, alpha)
        values = self._enforce_envelope(values, progress)
        if spec.drive_exit and 0.568 <= progress < spec.drive_stop:
            allowed = torch.arange(78, device=values.device) == 75
            values = values.masked_fill(~allowed, -torch.inf)
        self.current["changed"] += int(values.argmax() != original.argmax())
        return values

    def _integrate(self, features: torch.Tensor, alpha: float) -> torch.Tensor:
        count = self.experiment.quantiles
        points = (torch.arange(count, device=features.device) + 0.5) * (alpha / count)
        points = points.expand(features.shape[0], -1)
        support = ValueSupport(points, torch.full_like(points, 1.0 / count))
        values = self.base.model.expected_all_actions(features, support, RiskSpec())
        return self.base._mask(values)

    def _enforce_envelope(self, values: torch.Tensor, progress: float) -> torch.Tensor:
        spec = self.experiment
        if not spec.envelope or not spec.start <= progress < spec.stop:
            return values
        allowed = self.envelope[min(199, max(0, int(progress * 200)))]
        masked = values.masked_fill(~allowed, -torch.inf)
        if not torch.isfinite(masked).any():
            return values
        self.current["envelope_changes"] += int(masked.argmax() != values.argmax())
        return masked

    def _trace(self, observation: Any, action: int) -> None:
        physics = observation["physics"]
        context = observation["context"]
        self.current["trace"].append(
            [float(physics[3]), float(physics[0]), float(context[0]), action]
        )

    @property
    def last_q_margin(self) -> float | None:
        return self.base.last_q_margin

    @property
    def last_q_max(self) -> float | None:
        return self.base.last_q_max

    def export_state(self) -> Mapping[str, Any]:
        return self.base.export_state()

    def load_state(self, state: Mapping[str, Any]) -> None:
        self.base.load_state(state)
