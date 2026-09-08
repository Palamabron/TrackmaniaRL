from __future__ import annotations

import argparse
from itertools import product
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import numpy as np
import pytest
import torch

from trackmaniarl.commands import recovery_finetune_data as data_builder
from trackmaniarl.commands.recovery_finetune import (
    _model_actions,
    _RecoveryEpisode,
    _resolve_recovery_paths,
    _settings,
)
from trackmaniarl.commands.recovery_finetune_types import (
    _FineTuneSettings,
    _RecoverySample,
)
from trackmaniarl.trackmania.environment import TrackmaniaEnvironmentConfig


def _sample(
    identifier: int = 0,
    **values: float | int,
) -> _RecoverySample:
    return _RecoverySample(
        {"feature": torch.tensor([float(identifier)])},
        int(values.get("action", 0)),
        float(values.get("gate", 1.0)),
        int(values.get("source_action", 0)),
        float(values.get("elapsed_s", 0.0)),
    )


def _episode(
    path: str,
    sample_count: int = 0,
    **values: float | tuple[int, int, int],
) -> _RecoveryEpisode:
    samples = tuple(_sample(index) for index in range(sample_count))
    normalized_time_s = float(values.get("normalized_time_s", 0.0))
    stratum = cast(tuple[int, int, int], values.get("stratum", (0, 0, 0)))
    return _RecoveryEpisode(Path(path), samples, 40.0, normalized_time_s, stratum)


def _stratified_episodes(
    count: int, sample_count: int = 0, *, prefix: str = "episode"
) -> tuple[_RecoveryEpisode, ...]:
    cells = tuple(product(range(3), repeat=2))
    return tuple(
        _episode(
            f"{prefix}-{index}.npz",
            sample_count,
            stratum=(*cells[index % len(cells)], (index // len(cells)) % 2),
        )
        for index in range(count)
    )


def _settings_namespace(**overrides: int | float) -> argparse.Namespace:
    values: dict[str, int | float] = {
        "updates": 300,
        "batch_size": 128,
        "validation_fraction": 0.25,
        "minimum_gate": 0.01,
        "log_interval": 25,
        "minimum_usable_episodes": 24,
        "minimum_validation_episodes": 6,
        "minimum_gated_samples": 500,
        "minimum_samples_per_episode": 15,
        "maximum_normalized_recovery_time": 80.0,
        "minimum_source_disagreement": 0.05,
        "maximum_source_disagreement": 0.20,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def _default_settings(**overrides: int | float) -> _FineTuneSettings:
    return _settings(_settings_namespace(**overrides))


class _StreamingPipeline:
    def __init__(self) -> None:
        self.reset_count = 0
        self.frames: list[int] = []

    def reset_episode(self) -> None:
        self.reset_count += 1

    def transform_observation(self, frame: np.ndarray) -> dict[str, torch.Tensor]:
        self.frames.append(int(frame[0]))
        return {"feature": torch.tensor([frame[0]]), "recovery": torch.tensor([frame[0]])}


class _StreamingInference:
    def __init__(self) -> None:
        self.gate_batches: list[int] = []
        self.source_batches: list[int] = []

    def incident_gates(self, _learner: Any, observations: tuple[Any, ...]) -> np.ndarray:
        self.gate_batches.append(len(observations))
        return np.asarray(
            [float(observation["feature"].item() % 2) for observation in observations],
            dtype=np.float32,
        )

    def source_actions(self, _learner: Any, observations: tuple[Any, ...]) -> np.ndarray:
        self.source_batches.append(len(observations))
        return np.asarray(
            [int(observation["feature"].item()) + 10 for observation in observations],
            dtype=np.int64,
        )


def _configure_streaming_inference(
    monkeypatch: pytest.MonkeyPatch, inference: _StreamingInference
) -> None:
    monkeypatch.setattr(data_builder, "_RECOVERY_INFERENCE_BATCH_SIZE", 2)
    monkeypatch.setattr(data_builder, "_incident_gates", inference.incident_gates)
    monkeypatch.setattr(data_builder, "_source_actions", inference.source_actions)


def _streaming_request(pipeline: _StreamingPipeline) -> data_builder._StreamingPostTakeover:
    frames = np.zeros((8, 33), dtype=np.float32)
    frames[:, 0] = np.arange(len(frames))
    frames[:, 3] = np.arange(len(frames)) * 50.0
    return data_builder._StreamingPostTakeover(
        cast(Any, pipeline), cast(Any, object()), frames, np.arange(7, dtype=np.int64), 3, 0.5
    )


def _assert_streamed_samples(
    pipeline: _StreamingPipeline,
    inference: _StreamingInference,
    samples: tuple[_RecoverySample, ...],
) -> None:
    assert pipeline.reset_count == 1
    assert pipeline.frames == list(range(7))
    assert inference.gate_batches == [2, 2]
    assert inference.source_batches == [1, 1]
    assert [sample.action for sample in samples] == [3, 5]
    assert [sample.source_action for sample in samples] == [13, 15]
    assert [sample.takeover_elapsed_s for sample in samples] == [0.0, 0.1]


class _ChunkedInference:
    def __init__(self) -> None:
        self.source_batches: list[int] = []
        self.gate_batches: list[int] = []

    def predictions(self, batch: Any) -> torch.Tensor:
        self.source_batches.append(len(batch["feature"]))
        return torch.zeros(len(batch["feature"]), dtype=torch.int64)

    def incident_gate(self, recovery: torch.Tensor) -> torch.Tensor:
        self.gate_batches.append(len(recovery))
        return torch.ones((len(recovery), 1))


def _chunked_observations() -> tuple[dict[str, torch.Tensor], ...]:
    return tuple(
        {"feature": torch.tensor([float(index)]), "recovery": torch.tensor([float(index)])}
        for index in range(5)
    )


def _chunked_learners(inference: _ChunkedInference) -> tuple[SimpleNamespace, SimpleNamespace]:
    source = SimpleNamespace(supervised_recovery_predictions=inference.predictions)
    gate = SimpleNamespace(
        model=SimpleNamespace(encoder=SimpleNamespace(incident_gate=inference.incident_gate)),
        device=torch.device("cpu"),
    )
    return source, gate


def _assert_chunked_inference(
    inference: _ChunkedInference, source_actions: np.ndarray, gates: np.ndarray
) -> None:
    assert inference.source_batches == [2, 2, 1]
    assert inference.gate_batches == [2, 2, 1]
    np.testing.assert_array_equal(source_actions, np.zeros(5, dtype=np.int64))
    np.testing.assert_array_equal(gates, np.ones(5, dtype=np.float32))


def test_recovery_paths_expand_directories_without_duplicates(tmp_path: Path) -> None:
    first = tmp_path / "a.npz"
    second = tmp_path / "nested" / "b.npz"
    second.parent.mkdir()
    first.touch()
    second.touch()

    paths = _resolve_recovery_paths((tmp_path, first))

    assert paths == (first.resolve(), second.resolve())


def test_recovery_stratum_uses_actual_incident_metadata() -> None:
    recovery = SimpleNamespace(
        actual_progress=0.65,
        actual_perturbation_duration_ms=100.0,
        perturbation_control=np.asarray([1.0, 0.0, -1.0]),
    )

    assert data_builder._recovery_stratum(cast(Any, recovery)) == (1, 0, 0)


def test_recovery_actions_map_canonical_ids_into_compact_model_space() -> None:
    config = TrackmaniaEnvironmentConfig(
        geometry_path=Path("geometry.npz"),
        expected_map_uid="map",
        compact_action_ids=(3, 39, 75),
    )

    actions = _model_actions(np.asarray([75, 3, 39]), config, action_count=3)

    np.testing.assert_array_equal(actions, np.asarray([2, 0, 1]))


def test_recovery_actions_reject_an_excluded_human_control() -> None:
    config = TrackmaniaEnvironmentConfig(
        geometry_path=Path("geometry.npz"),
        expected_map_uid="map",
        compact_action_ids=(3, 75),
    )

    with pytest.raises(ValueError, match="excluded"):
        _model_actions(np.asarray([39]), config, action_count=2)


def test_recovery_data_rejects_short_and_slow_episodes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    episodes = {
        Path("short.npz"): _episode("short.npz", 14, normalized_time_s=30.0),
        Path("slow.npz"): _episode("slow.npz", 15, normalized_time_s=80.01),
        Path("boundary.npz"): _episode("boundary.npz", 15, normalized_time_s=80.0),
    }
    monkeypatch.setattr(
        data_builder,
        "_load_episode",
        lambda path, _context: episodes[path],
    )

    usable = data_builder._usable_episodes(
        tuple(episodes), cast(Any, object()), _default_settings()
    )

    assert usable == (episodes[Path("boundary.npz")],)


def test_recovery_resampling_with_no_post_takeover_step_is_rejected_cleanly() -> None:
    samples = data_builder._stream_post_takeover_samples(
        data_builder._StreamingPostTakeover(
            cast(Any, object()),
            cast(Any, object()),
            np.zeros((2, 33), dtype=np.float32),
            np.asarray([0], dtype=np.int64),
            1,
            0.01,
        )
    )

    assert samples == ()


def test_recovery_data_streams_post_takeover_inference_in_bounded_batches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = _StreamingPipeline()
    inference = _StreamingInference()
    _configure_streaming_inference(monkeypatch, inference)
    samples = data_builder._stream_post_takeover_samples(_streaming_request(pipeline))
    _assert_streamed_samples(pipeline, inference, samples)


def test_recovery_inference_helpers_chunk_long_observation_sequences(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(data_builder, "_RECOVERY_INFERENCE_BATCH_SIZE", 2)
    inference = _ChunkedInference()
    source_learner, gate_learner = _chunked_learners(inference)
    observations = _chunked_observations()
    source_actions = data_builder._source_actions(cast(Any, source_learner), observations)
    gates = data_builder._incident_gates(cast(Any, gate_learner), observations)
    _assert_chunked_inference(inference, source_actions, gates)


def test_recovery_data_requires_24_episodes_500_samples_and_6_held_out() -> None:
    settings = _default_settings()
    too_few_episodes = _stratified_episodes(23, 22, prefix="few")
    too_few_samples = _stratified_episodes(24, 20, prefix="short")
    exact_minimum = _stratified_episodes(24, 21, prefix="ok")

    with pytest.raises(ValueError, match=r"23 usable episodes.*at least 24"):
        data_builder._require_dataset_size(too_few_episodes, settings)
    with pytest.raises(ValueError, match=r"480 gated samples.*at least 500"):
        data_builder._require_dataset_size(too_few_samples, settings)
    data_builder._require_dataset_size(exact_minimum, settings)
    with pytest.raises(ValueError, match=r"5 held-out episodes.*at least 6"):
        data_builder._require_validation_size(exact_minimum[:5], settings)
    data_builder._require_validation_size(exact_minimum[:6], settings)


def test_recovery_data_rejects_missing_actual_progress_severity_coverage() -> None:
    episodes = tuple(
        _episode(
            f"episode-{index}.npz",
            21,
            stratum=(index % 3, (index // 3) % 2, index % 2),
        )
        for index in range(24)
    )

    with pytest.raises(ValueError, match="actual progress/severity cell"):
        data_builder._require_dataset_size(episodes, _default_settings())


def test_recovery_build_splits_and_records_only_usable_episode_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    episodes = _stratified_episodes(24, 21)
    supplied = (*tuple(episode.path for episode in episodes), Path("rejected.npz"))
    monkeypatch.setattr(data_builder, "_usable_episodes", lambda *_args: episodes)
    context = cast(Any, SimpleNamespace(learner=SimpleNamespace(seed=17)))

    data = data_builder._build_recovery_data(supplied, context, _default_settings())

    assert data.train_episodes == 18
    assert data.validation_episodes == 6
    assert len(data.train) + len(data.validation) == 504
    assert set(data.paths) == {episode.path for episode in episodes}
    assert Path("rejected.npz") not in data.paths
