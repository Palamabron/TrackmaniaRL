from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import cast

import torch

from trackmaniarl.commands.recovery_finetune import _RecoveryEpisode, _split_episodes
from trackmaniarl.commands.recovery_finetune_types import _RecoverySample

_DIRECTION_COVERAGE_STRATA = (
    (0, 0, 1),
    (0, 0, 1),
    (0, 1, 0),
    (0, 1, 0),
    (0, 2, 1),
    (0, 2, 1),
    (1, 0, 1),
    (1, 0, 0),
    (1, 1, 0),
    (1, 1, 1),
    (1, 2, 1),
    (1, 2, 1),
    (2, 0, 1),
    (2, 0, 1),
    (2, 1, 1),
    (2, 1, 1),
    (2, 2, 0),
    (2, 2, 0),
    (2, 2, 1),
    (0, 2, 1),
    (2, 2, 0),
    (0, 0, 1),
    (1, 2, 0),
    (0, 2, 1),
)


def _sample(identifier: int = 0) -> _RecoverySample:
    return _RecoverySample({"feature": torch.tensor([float(identifier)])}, 0, 1.0, 0, 0.0)


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


def _base_cell(episode: _RecoveryEpisode) -> tuple[int, int]:
    return episode.stratum[:2]


def _direction_coverage_episodes() -> tuple[_RecoveryEpisode, ...]:
    return tuple(
        _episode(f"episode-{index}.npz", stratum=stratum)
        for index, stratum in enumerate(_DIRECTION_COVERAGE_STRATA)
    )


def test_recovery_split_is_episode_level_and_deterministic() -> None:
    episodes = _stratified_episodes(36)

    first = _split_episodes(episodes, 0.25, 17)
    second = _split_episodes(episodes, 0.25, 17)

    assert first == second
    assert len(first[0]) == 27
    assert len(first[1]) == 9
    assert set(first[0]).isdisjoint(first[1])
    assert {_base_cell(episode) for episode in first[1]} == set(product(range(3), repeat=2))
    assert {episode.stratum[2] for episode in first[1]} == {0, 1}


def test_recovery_split_balances_actual_marginals_at_minimum_dataset_size() -> None:
    training_split, validation = _split_episodes(_stratified_episodes(24), 0.25, 17)

    assert len(validation) == 6
    assert [sum(episode.stratum[0] == value for episode in validation) for value in range(3)] == [
        2,
        2,
        2,
    ]
    assert [sum(episode.stratum[1] == value for episode in validation) for value in range(3)] == [
        2,
        2,
        2,
    ]
    assert {episode.stratum[2] for episode in validation} == {0, 1}
    assert {_base_cell(episode) for episode in training_split} == set(product(range(3), repeat=2))


def test_recovery_split_jointly_preserves_direction_coverage() -> None:
    training_split, validation = _split_episodes(_direction_coverage_episodes(), 0.25, 17)

    assert {episode.stratum[2] for episode in training_split} == {0, 1}
    assert {episode.stratum[2] for episode in validation} == {0, 1}
