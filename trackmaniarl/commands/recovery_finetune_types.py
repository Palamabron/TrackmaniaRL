"""Internal data structures for supervised recovery fine-tuning."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trackmaniarl.core.pytree import PyTree
from trackmaniarl.experiments.graph_iqn_v5 import BoundaryGraphFeaturePipelineV5
from trackmaniarl.experiments.graph_iqn_v6 import (
    IncidentRecoveryOnlyDiscreteValueLearner,
)
from trackmaniarl.trackmania.environment import TrackmaniaEnvironmentConfig
from trackmaniarl.trackmania.geometry import BoundaryGeometry

type _RecoveryStratum = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class _RecoverySample:
    observation: PyTree
    action: int
    gate: float
    source_action: int
    takeover_elapsed_s: float


@dataclass(frozen=True, slots=True)
class _RecoveryEpisode:
    path: Path
    samples: tuple[_RecoverySample, ...]
    finish_time_s: float
    normalized_recovery_time_s: float = 0.0
    stratum: _RecoveryStratum = (0, 0, 0)


@dataclass(frozen=True, slots=True)
class _RecoveryData:
    train: tuple[_RecoverySample, ...]
    validation: tuple[_RecoverySample, ...]
    train_by_episode: tuple[tuple[_RecoverySample, ...], ...]
    validation_by_episode: tuple[tuple[_RecoverySample, ...], ...]
    train_episodes: int
    validation_episodes: int
    paths: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class _FineTuneSettings:
    updates: int
    batch_size: int
    validation_fraction: float
    minimum_gate: float
    log_interval: int
    minimum_usable_episodes: int
    minimum_validation_episodes: int
    minimum_gated_samples: int
    minimum_samples_per_episode: int
    maximum_normalized_recovery_time_s: float
    minimum_source_disagreement: float
    maximum_source_disagreement: float


@dataclass(frozen=True, slots=True)
class _FineTuneResult:
    best_update: int
    train_metrics: Mapping[str, float]
    validation_metrics: Mapping[str, float] | None


@dataclass(frozen=True, slots=True)
class _RecoveryBuildContext:
    config: TrackmaniaEnvironmentConfig
    geometry: BoundaryGeometry
    pipeline: BoundaryGraphFeaturePipelineV5
    learner: IncidentRecoveryOnlyDiscreteValueLearner
    minimum_gate: float
    source_checkpoint_sha256: str


@dataclass(frozen=True, slots=True)
class _CheckpointRequest:
    source: Path
    data: _RecoveryData
    settings: _FineTuneSettings
    result: _FineTuneResult
    output: Path | None


@dataclass(frozen=True, slots=True)
class _FineTuneContext:
    learner: IncidentRecoveryOnlyDiscreteValueLearner
    settings: _FineTuneSettings
    logger: Any


__all__ = [
    "_CheckpointRequest",
    "_FineTuneContext",
    "_FineTuneResult",
    "_FineTuneSettings",
    "_RecoveryBuildContext",
    "_RecoveryData",
    "_RecoveryEpisode",
    "_RecoverySample",
    "_RecoveryStratum",
]
