"""Build supervised samples from causal human recovery episodes."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
import torch

from trackmaniarl.commands.recovery_finetune_strata import (
    recovery_stratum as _recovery_stratum,
)
from trackmaniarl.commands.recovery_finetune_strata import (
    require_stratified_coverage as _require_stratified_coverage,
)
from trackmaniarl.commands.recovery_finetune_strata import split_episodes as _split_episodes
from trackmaniarl.commands.recovery_finetune_types import (
    _FineTuneSettings,
    _RecoveryBuildContext,
    _RecoveryData,
    _RecoveryEpisode,
    _RecoverySample,
)
from trackmaniarl.core.pytree import PyTree, sanitize_finite, tree_collate
from trackmaniarl.experiments.graph_iqn_v5 import BoundaryGraphFeaturePipelineV5
from trackmaniarl.experiments.graph_iqn_v6 import (
    IncidentGatedTrackGnnSimbaEncoderV6,
    IncidentRecoveryOnlyDiscreteValueLearner,
)
from trackmaniarl.trackmania.demonstration_processing import validate_demonstration
from trackmaniarl.trackmania.demonstration_transitions import (
    resample_demonstration_for_environment,
)
from trackmaniarl.trackmania.environment import TrackmaniaEnvironmentConfig
from trackmaniarl.trackmania.human_recovery import (
    RecoveryDemonstration,
    load_recovery_demonstration,
)

_RECOVERY_INFERENCE_BATCH_SIZE = 256


@dataclass(frozen=True, slots=True)
class _StreamingPostTakeover:
    pipeline: BoundaryGraphFeaturePipelineV5
    learner: IncidentRecoveryOnlyDiscreteValueLearner
    frames: np.ndarray
    actions: np.ndarray
    takeover: int
    minimum_gate: float


@dataclass(frozen=True, slots=True)
class _PostTakeoverBatch:
    observations: tuple[PyTree, ...]
    actions: np.ndarray
    times_ms: np.ndarray
    takeover_time_ms: float


@dataclass(frozen=True, slots=True)
class _GatedPostTakeoverBatch:
    batch: _PostTakeoverBatch
    gates: np.ndarray


def _resolve_recovery_paths(values: Sequence[Path]) -> tuple[Path, ...]:
    paths = [path for value in values for path in _paths_for_value(value)]
    unique = tuple(dict.fromkeys(paths))
    if not unique:
        raise FileNotFoundError("no human recovery .npz archives were found")
    return unique


def _paths_for_value(value: Path) -> tuple[Path, ...]:
    if value.is_dir():
        return tuple(sorted(path.resolve() for path in value.rglob("*.npz")))
    if value.is_file() and value.suffix.lower() == ".npz":
        return (value.resolve(),)
    raise FileNotFoundError(f"recovery path is not an .npz file or directory: {value}")


def _build_recovery_data(
    paths: tuple[Path, ...],
    context: _RecoveryBuildContext,
    settings: _FineTuneSettings,
) -> _RecoveryData:
    episodes = _usable_episodes(paths, context, settings)
    _require_dataset_size(episodes, settings)
    seed = context.learner.seed
    training, validation = _split_episodes(episodes, settings.validation_fraction, seed)
    _require_validation_size(validation, settings)
    return _recovery_data(training, validation)


def _recovery_data(
    training: tuple[_RecoveryEpisode, ...], validation: tuple[_RecoveryEpisode, ...]
) -> _RecoveryData:
    return _RecoveryData(
        _flatten_samples(training),
        _flatten_samples(validation),
        tuple(episode.samples for episode in training),
        tuple(episode.samples for episode in validation),
        len(training),
        len(validation),
        tuple(episode.path for episode in (*training, *validation)),
    )


def _usable_episodes(
    paths: tuple[Path, ...],
    context: _RecoveryBuildContext,
    settings: _FineTuneSettings,
) -> tuple[_RecoveryEpisode, ...]:
    loaded = tuple(_load_episode(path, context) for path in paths)
    gated = tuple(
        episode
        for episode in loaded
        if len(episode.samples) >= settings.minimum_samples_per_episode
    )
    episodes = tuple(
        episode
        for episode in gated
        if episode.normalized_recovery_time_s <= settings.maximum_normalized_recovery_time_s
    )
    _report_rejected(len(loaded) - len(gated), len(gated) - len(episodes))
    _require_usable_episodes(episodes)
    return episodes


def _require_usable_episodes(episodes: tuple[_RecoveryEpisode, ...]) -> None:
    if not episodes:
        raise ValueError("human recovery data has no usable post-takeover episodes")


def _report_rejected(gate_rejected: int, quality_rejected: int) -> None:
    if gate_rejected:
        print(
            f"Skipped {gate_rejected} recovery archive(s) with too few active "
            "post-takeover incident-gate samples."
        )
    if quality_rejected:
        print(f"Skipped {quality_rejected} recovery archive(s) that failed the pace-quality gate.")


def _require_dataset_size(
    episodes: tuple[_RecoveryEpisode, ...], settings: _FineTuneSettings
) -> None:
    samples = sum(len(episode.samples) for episode in episodes)
    if len(episodes) < settings.minimum_usable_episodes:
        raise ValueError(
            f"recovery data has {len(episodes)} usable episodes; "
            f"requires at least {settings.minimum_usable_episodes}"
        )
    if samples < settings.minimum_gated_samples:
        raise ValueError(
            f"recovery data has {samples} gated samples; "
            f"requires at least {settings.minimum_gated_samples}"
        )
    _require_stratified_coverage(episodes)


def _require_validation_size(
    episodes: tuple[_RecoveryEpisode, ...], settings: _FineTuneSettings
) -> None:
    if len(episodes) < settings.minimum_validation_episodes:
        raise ValueError(
            f"recovery validation has {len(episodes)} held-out episodes; "
            f"requires at least {settings.minimum_validation_episodes}"
        )


def _flatten_samples(
    episodes: tuple[_RecoveryEpisode, ...],
) -> tuple[_RecoverySample, ...]:
    return tuple(sample for episode in episodes for sample in episode.samples)


def _load_episode(path: Path, context: _RecoveryBuildContext) -> _RecoveryEpisode:
    recovery = _validated_recovery(path, context)
    demonstration = recovery.demonstration
    frames, actions = resample_demonstration_for_environment(demonstration, context.config)
    model_actions = _model_actions(actions, context.config, context.learner.model.action_count)
    takeover = _takeover_index(recovery, frames)
    samples = _stream_post_takeover_samples(
        _StreamingPostTakeover(
            context.pipeline,
            context.learner,
            frames,
            model_actions,
            takeover,
            context.minimum_gate,
        )
    )
    normalized = _normalized_recovery_time_s(recovery)
    stratum = _recovery_stratum(recovery)
    return _RecoveryEpisode(path, samples, demonstration.finish_time_s, normalized, stratum)


def _normalized_recovery_time_s(recovery: RecoveryDemonstration) -> float:
    demonstration = recovery.demonstration
    takeover_s = float(demonstration.frames[recovery.takeover_step, 3]) / 1_000.0
    elapsed_s = max(0.0, demonstration.finish_time_s - takeover_s)
    remaining = max(1.0e-6, 1.0 - recovery.actual_progress)
    return elapsed_s / remaining


def _validated_recovery(path: Path, context: _RecoveryBuildContext) -> RecoveryDemonstration:
    recovery = load_recovery_demonstration(path)
    if recovery.source_checkpoint_sha256 != context.source_checkpoint_sha256:
        raise ValueError(
            f"recovery archive checkpoint provenance does not match the source policy: {path}"
        )
    validate_demonstration(recovery.demonstration, context.config, context.geometry)
    return recovery


def _takeover_index(recovery: RecoveryDemonstration, frames: np.ndarray) -> int:
    source_frames = recovery.demonstration.frames
    takeover_time_ms = float(source_frames[recovery.takeover_step, 3])
    return int(np.searchsorted(frames[:-1, 3], takeover_time_ms, side="left"))


def _stream_post_takeover_samples(
    request: _StreamingPostTakeover,
) -> tuple[_RecoverySample, ...]:
    """Build only gated post-takeover samples, keeping inference batches bounded."""

    if request.takeover >= len(request.actions):
        return ()
    takeover_time_ms = _prepare_post_takeover_stream(request)
    return tuple(
        sample
        for batch in _post_takeover_batches(request, takeover_time_ms)
        for sample in _gated_batch_samples(request.learner, batch, request.minimum_gate)
    )


def _prepare_post_takeover_stream(request: _StreamingPostTakeover) -> float:
    request.pipeline.reset_episode()
    for frame in request.frames[: request.takeover]:
        _episode_observation(request.pipeline, frame)
    return float(request.frames[request.takeover, 3])


def _post_takeover_batches(
    request: _StreamingPostTakeover, takeover_time_ms: float
) -> Iterator[_PostTakeoverBatch]:
    for start in range(request.takeover, len(request.actions), _RECOVERY_INFERENCE_BATCH_SIZE):
        yield _post_takeover_batch(request, start, takeover_time_ms)


def _post_takeover_batch(
    request: _StreamingPostTakeover, start: int, takeover_time_ms: float
) -> _PostTakeoverBatch:
    stop = min(start + _RECOVERY_INFERENCE_BATCH_SIZE, len(request.actions))
    observations = tuple(
        _episode_observation(request.pipeline, frame) for frame in request.frames[start:stop]
    )
    return _PostTakeoverBatch(
        observations, request.actions[start:stop], request.frames[start:stop, 3], takeover_time_ms
    )


def _gated_batch_samples(
    learner: IncidentRecoveryOnlyDiscreteValueLearner,
    batch: _PostTakeoverBatch,
    minimum_gate: float,
) -> tuple[_RecoverySample, ...]:
    gated = _GatedPostTakeoverBatch(batch, _incident_gates(learner, batch.observations))
    indices = _selected_indices(gated.gates, minimum_gate)
    sources = _source_actions(learner, _selected_observations(batch, indices))
    return tuple(
        _batch_recovery_sample(gated, index, source)
        for index, source in zip(indices, sources, strict=True)
    )


def _selected_indices(gates: np.ndarray, minimum_gate: float) -> tuple[int, ...]:
    return tuple(index for index, gate in enumerate(gates) if float(gate) > minimum_gate)


def _selected_observations(
    batch: _PostTakeoverBatch, indices: tuple[int, ...]
) -> tuple[PyTree, ...]:
    return tuple(batch.observations[index] for index in indices)


def _batch_recovery_sample(
    gated: _GatedPostTakeoverBatch, index: int, source_action: np.int64
) -> _RecoverySample:
    batch = gated.batch
    elapsed_s = (float(batch.times_ms[index]) - batch.takeover_time_ms) / 1_000.0
    return _RecoverySample(
        batch.observations[index],
        int(batch.actions[index]),
        float(gated.gates[index]),
        int(source_action),
        max(0.0, elapsed_s),
    )


def _source_actions(
    learner: IncidentRecoveryOnlyDiscreteValueLearner,
    observations: tuple[PyTree, ...],
) -> np.ndarray:
    if not observations:
        return np.empty(0, dtype=np.int64)
    outputs = [
        _source_action_batch(learner, observations[start : start + _RECOVERY_INFERENCE_BATCH_SIZE])
        for start in range(0, len(observations), _RECOVERY_INFERENCE_BATCH_SIZE)
    ]
    return _concatenate_inference_outputs(outputs)


def _source_action_batch(
    learner: IncidentRecoveryOnlyDiscreteValueLearner,
    observations: tuple[PyTree, ...],
) -> np.ndarray:
    batch = cast(Mapping[str, torch.Tensor], tree_collate(list(observations)))
    return learner.supervised_recovery_predictions(batch).numpy().astype(np.int64, copy=False)


def _episode_observation(pipeline: BoundaryGraphFeaturePipelineV5, frame: np.ndarray) -> PyTree:
    return sanitize_finite(pipeline.transform_observation(frame))


def _incident_gates(
    learner: IncidentRecoveryOnlyDiscreteValueLearner,
    observations: tuple[PyTree, ...],
) -> np.ndarray:
    if not observations:
        return np.empty(0, dtype=np.float32)
    encoder = cast(IncidentGatedTrackGnnSimbaEncoderV6, learner.model.encoder)
    outputs: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(observations), _RECOVERY_INFERENCE_BATCH_SIZE):
            batch = observations[start : start + _RECOVERY_INFERENCE_BATCH_SIZE]
            recovery = torch.stack([observation["recovery"] for observation in batch])
            gates = encoder.incident_gate(recovery.to(learner.device)).squeeze(-1)
            outputs.append(gates.detach().float().cpu().numpy())
    return _concatenate_inference_outputs(outputs)


def _concatenate_inference_outputs(outputs: list[np.ndarray]) -> np.ndarray:
    return outputs[0] if len(outputs) == 1 else np.concatenate(outputs)


def _model_actions(
    actions: np.ndarray,
    config: TrackmaniaEnvironmentConfig,
    action_count: int,
) -> np.ndarray:
    result = _compact_actions(actions, config.compact_action_ids)
    if np.any(result < 0) or np.any(result >= action_count):
        raise ValueError("human recovery action is outside the configured model action space")
    return result


def _compact_actions(actions: np.ndarray, compact: tuple[int, ...] | None) -> np.ndarray:
    if compact is None:
        return np.asarray(actions, dtype=np.int64)
    indices = {source: index for index, source in enumerate(compact)}
    missing = sorted(set(map(int, actions)) - indices.keys())
    if missing:
        raise ValueError(f"human recovery uses actions excluded by compact_action_ids: {missing}")
    return np.asarray([indices[int(action)] for action in actions], dtype=np.int64)


__all__ = [
    "_build_recovery_data",
    "_model_actions",
    "_resolve_recovery_paths",
    "_split_episodes",
]
