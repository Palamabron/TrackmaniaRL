"""Optimization and checkpoint persistence for recovery fine-tuning."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from math import exp
from typing import Any, cast

import torch

from trackmaniarl.commands.recovery_finetune_types import (
    _FineTuneContext,
    _FineTuneResult,
    _FineTuneSettings,
    _RecoveryData,
    _RecoverySample,
)
from trackmaniarl.core.pytree import tree_collate
from trackmaniarl.experiments.graph_iqn_v6 import (
    IncidentRecoveryOnlyDiscreteValueLearner,
)


@dataclass(frozen=True, slots=True)
class _FineTuneLoop:
    data: _RecoveryData
    context: _FineTuneContext
    generator: torch.Generator


@dataclass(frozen=True, slots=True)
class _FineTuneStep:
    update: int
    train: Mapping[str, float]
    validation: Mapping[str, float] | None


@dataclass(frozen=True, slots=True)
class _BestCandidate:
    update: int
    score: tuple[float, float] | None
    baseline_accuracy: float
    validation: Mapping[str, float] | None
    adapter: Mapping[str, Any]


def _settings(args: argparse.Namespace) -> _FineTuneSettings:
    settings = _FineTuneSettings(
        int(args.updates),
        int(args.batch_size),
        float(args.validation_fraction),
        float(args.minimum_gate),
        int(args.log_interval),
        int(args.minimum_usable_episodes),
        int(args.minimum_validation_episodes),
        int(args.minimum_gated_samples),
        int(args.minimum_samples_per_episode),
        float(args.maximum_normalized_recovery_time),
        float(args.minimum_source_disagreement),
        float(args.maximum_source_disagreement),
    )
    _validate_settings(settings)
    return settings


def _validate_settings(settings: _FineTuneSettings) -> None:
    _validate_optimization_settings(settings)
    _validate_data_settings(settings)


def _validate_optimization_settings(settings: _FineTuneSettings) -> None:
    if settings.updates < 1 or settings.batch_size < 1 or settings.log_interval < 1:
        raise ValueError("recovery updates, batch size and log interval must be positive")
    if not 0.0 <= settings.validation_fraction < 1.0:
        raise ValueError("recovery validation fraction must be in [0, 1)")
    if not 0.0 <= settings.minimum_gate <= 1.0:
        raise ValueError("recovery minimum gate must be in [0, 1]")


def _validate_data_settings(settings: _FineTuneSettings) -> None:
    _validate_data_minimums(settings)
    if settings.minimum_validation_episodes >= settings.minimum_usable_episodes:
        raise ValueError("recovery validation minimum must be below the usable-episode minimum")
    if settings.validation_fraction <= 0.0:
        raise ValueError("recovery fine-tuning requires episode-held-out validation")
    if settings.maximum_normalized_recovery_time_s <= 0.0:
        raise ValueError("maximum normalized recovery time must be positive")
    _validate_disagreement_bounds(settings)


def _validate_data_minimums(settings: _FineTuneSettings) -> None:
    counts = (
        settings.minimum_usable_episodes,
        settings.minimum_validation_episodes,
        settings.minimum_gated_samples,
        settings.minimum_samples_per_episode,
    )
    if any(value < 1 for value in counts):
        raise ValueError("recovery data minimums must be positive")


def _validate_disagreement_bounds(settings: _FineTuneSettings) -> None:
    disagreement = (
        settings.minimum_source_disagreement,
        settings.maximum_source_disagreement,
    )
    if not 0.0 <= disagreement[0] < disagreement[1] <= 1.0:
        raise ValueError("recovery source-disagreement bounds must satisfy 0 <= min < max <= 1")


def _fine_tune(data: _RecoveryData, context: _FineTuneContext) -> _FineTuneResult:
    generator = torch.Generator(device="cpu").manual_seed(context.learner.seed)
    loop = _FineTuneLoop(data, context, generator)
    candidate = _initial_candidate(loop)
    for update in range(1, context.settings.updates + 1):
        step = _train_step(loop, update)
        candidate = _select_candidate(context, candidate, step)
        _log_step(loop, step)
    return _finish_fine_tune(loop, candidate)


def _initial_candidate(loop: _FineTuneLoop) -> _BestCandidate:
    settings = loop.context.settings
    validation = _evaluate_episodes(
        loop.context.learner, loop.data.validation_by_episode, settings.batch_size
    )
    adapter = deepcopy(loop.context.learner.model.encoder.recovery_adapter.state_dict())
    accuracy = 0.0 if validation is None else float(validation["recovery/action_accuracy"])
    return _BestCandidate(0, None, accuracy, validation, adapter)


def _train_step(loop: _FineTuneLoop, update: int) -> _FineTuneStep:
    settings = loop.context.settings
    samples = _sample_batch(loop.data.train_by_episode, settings.batch_size, loop.generator)
    batch = _batch_tensors(samples)
    loop.context.learner.supervised_recovery_update(*batch)
    train = _batch_metrics(loop.context.learner, samples)
    validation = _maybe_validate(loop.context, loop.data, update)
    return _FineTuneStep(update, train, validation)


def _select_candidate(
    context: _FineTuneContext,
    candidate: _BestCandidate,
    step: _FineTuneStep,
) -> _BestCandidate:
    score = _candidate_score(step.validation, candidate.baseline_accuracy, context.settings)
    if score is None or (candidate.score is not None and score <= candidate.score):
        return candidate
    adapter = deepcopy(context.learner.model.encoder.recovery_adapter.state_dict())
    return _BestCandidate(step.update, score, candidate.baseline_accuracy, step.validation, adapter)


def _candidate_score(
    metrics: Mapping[str, float] | None,
    baseline_accuracy: float,
    settings: _FineTuneSettings,
) -> tuple[float, float] | None:
    if metrics is None:
        return None
    disagreement = float(metrics["recovery/source_disagreement"])
    if not (
        settings.minimum_source_disagreement <= disagreement <= settings.maximum_source_disagreement
    ):
        return None
    accuracy = float(metrics["recovery/action_accuracy"])
    if accuracy <= baseline_accuracy:
        return None
    return accuracy, -float(metrics["recovery/loss"])


def _log_step(loop: _FineTuneLoop, step: _FineTuneStep) -> None:
    settings = loop.context.settings
    if step.update % settings.log_interval and step.update != settings.updates:
        return
    payload = {**step.train, **_validation_payload(step.validation)}
    loop.context.logger.log(
        "recovery/update", {**payload, "recovery/update": step.update}, step=step.update
    )


def _finish_fine_tune(
    loop: _FineTuneLoop,
    candidate: _BestCandidate,
) -> _FineTuneResult:
    _restore_candidate(loop, candidate)
    train_metrics = _required_training_metrics(loop)
    validation = _evaluate_episode_set(loop, loop.data.validation_by_episode)
    return _FineTuneResult(candidate.update, train_metrics, validation)


def _restore_candidate(loop: _FineTuneLoop, candidate: _BestCandidate) -> None:
    adapter = loop.context.learner.model.encoder.recovery_adapter
    adapter.load_state_dict(candidate.adapter, strict=True)


def _required_training_metrics(loop: _FineTuneLoop) -> Mapping[str, float]:
    train_metrics = _evaluate_episode_set(loop, loop.data.train_by_episode)
    if train_metrics is None:
        raise RuntimeError("recovery fine-tuning requires non-empty training episodes")
    return train_metrics


def _evaluate_episode_set(
    loop: _FineTuneLoop, episodes: tuple[tuple[_RecoverySample, ...], ...]
) -> Mapping[str, float] | None:
    return _evaluate_episodes(
        loop.context.learner,
        episodes,
        loop.context.settings.batch_size,
    )


def _sample_batch(
    episodes: tuple[tuple[_RecoverySample, ...], ...],
    batch_size: int,
    generator: torch.Generator,
) -> tuple[_RecoverySample, ...]:
    indices = torch.randint(len(episodes), (batch_size,), generator=generator).tolist()
    return tuple(_sample_episode(episodes[index], generator) for index in indices)


def _sample_episode(
    samples: tuple[_RecoverySample, ...], generator: torch.Generator
) -> _RecoverySample:
    weights = torch.tensor(
        [max(item.gate, 1.0e-6) * exp(-item.takeover_elapsed_s / 2.0) for item in samples]
    )
    index = int(torch.multinomial(weights, 1, generator=generator).item())
    return samples[index]


def _batch_tensors(
    samples: tuple[_RecoverySample, ...],
) -> tuple[Mapping[str, torch.Tensor], torch.Tensor]:
    observations = _collate_observations(samples)
    actions = torch.tensor([item.action for item in samples], dtype=torch.int64)
    return observations, actions


def _collate_observations(
    samples: list[_RecoverySample] | tuple[_RecoverySample, ...],
) -> Mapping[str, torch.Tensor]:
    return cast(Mapping[str, torch.Tensor], tree_collate([item.observation for item in samples]))


def _maybe_validate(
    context: _FineTuneContext, data: _RecoveryData, update: int
) -> Mapping[str, float] | None:
    if not data.validation:
        return None
    settings = context.settings
    if update % settings.log_interval and update != settings.updates:
        return None
    return _evaluate_episodes(context.learner, data.validation_by_episode, settings.batch_size)


def _evaluate_episodes(
    learner: IncidentRecoveryOnlyDiscreteValueLearner,
    episodes: tuple[tuple[_RecoverySample, ...], ...],
    batch_size: int,
) -> Mapping[str, float] | None:
    if not episodes:
        return None
    totals: dict[str, float] = {}
    for samples in episodes:
        metrics = _evaluate_samples(learner, samples, batch_size)
        _accumulate_metrics(totals, metrics, 1)
    return {key: value / len(episodes) for key, value in totals.items()}


def _evaluate_samples(
    learner: IncidentRecoveryOnlyDiscreteValueLearner,
    samples: tuple[_RecoverySample, ...],
    batch_size: int,
) -> Mapping[str, float]:
    weighted: dict[str, float] = {}
    for start in range(0, len(samples), batch_size):
        batch = samples[start : start + batch_size]
        _accumulate_metrics(weighted, _batch_metrics(learner, batch), len(batch))
    return {key: value / len(samples) for key, value in weighted.items()}


def _batch_metrics(
    learner: IncidentRecoveryOnlyDiscreteValueLearner,
    batch: tuple[_RecoverySample, ...],
) -> Mapping[str, float]:
    observations, actions = _batch_tensors(batch)
    metrics = dict(learner.supervised_recovery_metrics(observations, actions))
    predictions = learner.supervised_recovery_predictions(observations)
    sources = torch.tensor([item.source_action for item in batch], dtype=torch.int64)
    metrics["recovery/source_disagreement"] = float((predictions != sources).float().mean())
    metrics["recovery/gate_mean"] = sum(item.gate for item in batch) / len(batch)
    metrics["recovery/takeover_elapsed_s_mean"] = sum(
        item.takeover_elapsed_s for item in batch
    ) / len(batch)
    return metrics


def _accumulate_metrics(
    weighted: dict[str, float], metrics: Mapping[str, float], count: int
) -> None:
    for key, value in metrics.items():
        weighted[key] = weighted.get(key, 0.0) + value * count


def _validation_payload(metrics: Mapping[str, float] | None) -> dict[str, float]:
    if metrics is None:
        return {}
    return {
        f"recovery/validation_{key.removeprefix('recovery/')}": value
        for key, value in metrics.items()
    }


def _summary(data: _RecoveryData, result: _FineTuneResult) -> str:
    validation = _summary_validation(result.validation_metrics)
    return (
        "Recovery fine-tune complete: "
        f"train={len(data.train)} samples/{data.train_episodes} episodes, "
        f"validation={len(data.validation)} samples/{data.validation_episodes} episodes, "
        f"best_update={result.best_update}, {validation}"
    )


def _summary_validation(metrics: Mapping[str, float] | None) -> str:
    if metrics is None:
        return "validation=none"
    return (
        f"validation_loss={metrics['recovery/loss']:.4f}, "
        f"validation_accuracy={metrics['recovery/action_accuracy']:.3f}, "
        f"source_disagreement={metrics['recovery/source_disagreement']:.3f}"
    )


__all__ = [
    "_fine_tune",
    "_settings",
    "_summary",
]
