"""Optional objectives for discrete value learning."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise
from math import isfinite
from typing import Protocol

import torch


@dataclass(frozen=True, slots=True)
class ValueObjectiveContext:
    expected_values: torch.Tensor
    actions: torch.Tensor
    valid: torch.Tensor
    metadata: dict[str, object]
    action_mask: torch.Tensor | None = None


@dataclass(frozen=True, slots=True)
class _WeightedDemoLoss:
    context: ValueObjectiveContext
    losses: torch.Tensor
    valid: torch.Tensor


class ValueObjective(Protocol):
    requires_all_actions: bool

    def loss(self, context: ValueObjectiveContext) -> torch.Tensor | None: ...


class DemonstrationMarginObjective:
    requires_all_actions = True

    def __init__(
        self,
        margin: float = 0.8,
        weight: float = 1.0,
        steering_switch_weight: float = 1.0,
    ) -> None:
        _validate_non_negative(
            (margin, weight, steering_switch_weight), "demonstration margin and weights"
        )
        self.margin = margin
        self.weight = weight
        self.steering_switch_weight = steering_switch_weight

    def loss(self, context: ValueObjectiveContext) -> torch.Tensor | None:
        flags = context.metadata.get("expert_demo_flags", context.metadata.get("demo_flags"))
        if not self.weight:
            return None
        if flags is None:
            raise ValueError("demonstration margin objective requires demo_flags metadata")
        demo = _metadata_tensor(context, flags, torch.bool)
        expected = _masked_demo_values(context, demo)
        margins = torch.full_like(expected, self.margin).scatter(
            -1, context.actions.unsqueeze(-1), 0.0
        )
        expert = expected.gather(-1, context.actions.unsqueeze(-1)).squeeze(-1)
        losses = (expected + margins).amax(dim=-1) - expert
        valid = context.valid & demo
        return self.weight * _weighted_demo_mean(
            _WeightedDemoLoss(context, losses, valid),
            self.steering_switch_weight,
            0,
        )


class DemonstrationCrossEntropyObjective:
    requires_all_actions = True

    def __init__(
        self,
        weight: float = 1.0,
        steering_switch_weight: float = 1.0,
        steering_switch_radius_steps: int = 0,
    ) -> None:
        _validate_non_negative(
            (weight, steering_switch_weight), "demonstration cross-entropy weights"
        )
        self.weight = weight
        self.steering_switch_weight = steering_switch_weight
        self.steering_switch_radius_steps = _validate_switch_radius(steering_switch_radius_steps)

    def loss(self, context: ValueObjectiveContext) -> torch.Tensor | None:
        flags = context.metadata.get("demo_flags")
        if not self.weight:
            return None
        if flags is None:
            raise ValueError("demonstration cross-entropy objective requires demo_flags metadata")
        demo = _metadata_tensor(context, flags, torch.bool)
        expected = _masked_demo_values(context, demo)
        losses = _cross_entropy_losses(context, expected)
        valid = context.valid & demo
        return self.weight * _weighted_demo_mean(
            _WeightedDemoLoss(context, losses, valid),
            self.steering_switch_weight,
            self.steering_switch_radius_steps,
        )


class DemonstrationProgressWindowCrossEntropyObjective:
    """Imitate demonstrations only where track-local intervention is needed."""

    requires_all_actions = True

    def __init__(
        self,
        windows: Sequence[Sequence[float]],
        weight: float = 1.0,
    ) -> None:
        _validate_non_negative((weight,), "demonstration cross-entropy weight")
        self.windows = _validate_progress_windows(windows)
        self.weight = weight

    def loss(self, context: ValueObjectiveContext) -> torch.Tensor | None:
        if not self.weight:
            return None
        demo, progress = _demonstration_progress(context)
        in_window = _progress_window_mask(progress, self.windows)
        expected = _masked_demo_values(context, demo & in_window)
        losses = _cross_entropy_losses(context, expected)
        valid = context.valid & demo & in_window & torch.isfinite(progress)
        objective = _WeightedDemoLoss(context, losses, valid)
        return self.weight * _weighted_demo_mean(objective, 1.0, 0)


def _demonstration_progress(
    context: ValueObjectiveContext,
) -> tuple[torch.Tensor, torch.Tensor]:
    flags = context.metadata.get("demo_flags")
    values = context.metadata.get("demonstration_progress_fractions")
    if flags is None:
        raise ValueError("demonstration progress objective requires demo_flags metadata")
    if values is None:
        raise ValueError("demonstration progress objective requires progress metadata")
    return (
        _metadata_tensor(context, flags, torch.bool),
        _metadata_tensor(context, values, torch.float32),
    )


def _progress_window_mask(
    progress: torch.Tensor, windows: Sequence[tuple[float, float]]
) -> torch.Tensor:
    result = torch.zeros_like(progress, dtype=torch.bool)
    for start, end in windows:
        result |= (progress >= start) & (progress <= end)
    return result


def _cross_entropy_losses(context: ValueObjectiveContext, expected: torch.Tensor) -> torch.Tensor:
    losses = torch.nn.functional.cross_entropy(
        expected.reshape(-1, expected.shape[-1]),
        context.actions.reshape(-1),
        reduction="none",
    )
    return losses.reshape(context.actions.shape)


def _weighted_demo_mean(
    objective: _WeightedDemoLoss,
    steering_switch_weight: float,
    steering_switch_radius_steps: int,
) -> torch.Tensor:
    context = objective.context
    weights = torch.ones_like(objective.losses)
    mask = _switch_weight_mask(context, steering_switch_weight, steering_switch_radius_steps)
    if mask is not None:
        weights = torch.where(mask, steering_switch_weight, 1.0)
    selected = weights * objective.valid
    return (objective.losses * selected).sum() / selected.sum().clamp_min(1.0)


def _switch_weight_mask(
    context: ValueObjectiveContext, weight: float, radius: int
) -> torch.Tensor | None:
    if weight == 1.0:
        return None
    key = "demonstration_steering_switches"
    dtype = torch.bool
    if radius:
        key = "demonstration_steering_switch_distances"
        dtype = torch.int64
    values = context.metadata.get(key)
    if values is None:
        raise ValueError("steering-switch weighting requires demonstration switch metadata")
    mask = _metadata_tensor(context, values, dtype)
    return mask <= radius if radius else mask


def _validate_switch_radius(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("steering_switch_radius_steps must be a non-negative integer")
    return value


def _validate_progress_windows(
    windows: Sequence[Sequence[float]],
) -> tuple[tuple[float, float], ...]:
    result: list[tuple[float, float]] = []
    for window in windows:
        if len(window) != 2:
            raise ValueError("each demonstration progress window requires start and end")
        start, end = (float(value) for value in window)
        if not all(isfinite(value) for value in (start, end)) or not 0.0 <= start < end <= 1.0:
            raise ValueError("demonstration progress windows must satisfy 0 <= start < end <= 1")
        result.append((start, end))
    if not result:
        raise ValueError("at least one demonstration progress window is required")
    ordered = tuple(sorted(result))
    if any(current[0] <= previous[1] for previous, current in pairwise(ordered)):
        raise ValueError("demonstration progress windows must not overlap")
    return ordered


def _metadata_tensor(
    context: ValueObjectiveContext, values: object, dtype: torch.dtype
) -> torch.Tensor:
    tensor = torch.as_tensor(values, dtype=dtype, device=context.expected_values.device)
    if tensor.shape == context.actions.shape:
        return tensor
    if tensor.shape == context.actions.shape[:1]:
        return tensor.unsqueeze(1).expand_as(context.actions)
    if tensor.numel() == context.actions.numel():
        return tensor.reshape_as(context.actions)
    raise ValueError("demonstration metadata shape does not match actions")


def _validate_non_negative(values: tuple[float, ...], name: str) -> None:
    if not all(isfinite(value) and value >= 0.0 for value in values):
        raise ValueError(f"{name} must be finite and non-negative")


def _masked_demo_values(context: ValueObjectiveContext, demo: torch.Tensor) -> torch.Tensor:
    if context.action_mask is None:
        return context.expected_values
    allowed = context.action_mask[context.actions]
    if torch.any(context.valid & demo & ~allowed):
        raise ValueError("demonstration action is excluded by policy_action_ids")
    selected = context.valid & demo
    masked = context.expected_values.masked_fill(~context.action_mask, -torch.inf)
    # Objectives compute per-row losses before their selected rows are reduced.  Leaving
    # an excluded target at ``-inf`` on an unselected row creates ``inf * 0`` (or
    # ``nan * 0`` for the margin loss), which poisons the whole reduction.
    return torch.where(selected.unsqueeze(-1), masked, context.expected_values)


class PolicyAnchorObjective:
    requires_all_actions = True

    def __init__(self, weight: float = 1.0) -> None:
        _validate_non_negative((weight,), "policy anchor weight")
        self.weight = weight

    def loss(self, context: ValueObjectiveContext) -> torch.Tensor | None:
        values = context.metadata.get("policy_anchor_q_values")
        if values is None or not self.weight:
            return None
        anchor = torch.as_tensor(
            values,
            dtype=context.expected_values.dtype,
            device=context.expected_values.device,
        )
        if anchor.shape != context.expected_values.shape:
            raise ValueError("policy anchor values must match all-action value shape")
        advantages = context.expected_values - context.expected_values.mean(dim=-1, keepdim=True)
        anchor_advantages = anchor - anchor.mean(dim=-1, keepdim=True)
        losses = torch.nn.functional.smooth_l1_loss(
            advantages, anchor_advantages, reduction="none"
        ).mean(dim=-1)
        valid = context.valid.to(losses.dtype)
        return self.weight * (losses * valid).sum() / valid.sum().clamp_min(1.0)
