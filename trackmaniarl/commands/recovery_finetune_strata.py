"""Actual-incident coverage gates and episode-level stratified splitting."""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import combinations, product
from typing import NoReturn

from trackmaniarl.commands.recovery_finetune_types import (
    _RecoveryEpisode,
    _RecoveryStratum,
)
from trackmaniarl.trackmania.human_recovery import RecoveryDemonstration

_PROGRESS_BOUNDARIES = (0.65, 0.75)
_SEVERITY_BOUNDARIES_MS = (100.0, 150.0)
_EXPECTED_BASE_CELLS = frozenset(product(range(3), repeat=2))


@dataclass(frozen=True, slots=True)
class _SplitRequest:
    episodes: tuple[_RecoveryEpisode, ...]
    fraction: float
    seed: int


@dataclass(frozen=True, slots=True)
class _SplitContext:
    count: int
    fraction: float
    generator: random.Random


@dataclass(slots=True)
class _AllocationState:
    context: _SplitContext
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]]
    cells: list[tuple[int, int]]
    allocation: dict[tuple[int, int], int]


@dataclass(frozen=True, slots=True)
class _CellDirectionSelection:
    episodes: list[_RecoveryEpisode]
    count: int
    right_count: int


def recovery_stratum(recovery: RecoveryDemonstration) -> _RecoveryStratum:
    """Classify the incident that actually reached the game, not its requested plan."""

    progress = _ordinal_bin(recovery.actual_progress, _PROGRESS_BOUNDARIES)
    duration = recovery.actual_perturbation_duration_ms
    severity = int(duration > _SEVERITY_BOUNDARIES_MS[0]) + int(
        duration > _SEVERITY_BOUNDARIES_MS[1]
    )
    direction = int(float(recovery.perturbation_control[2]) > 0.0)
    return progress, severity, direction


def require_stratified_coverage(episodes: tuple[_RecoveryEpisode, ...]) -> None:
    """Require broad, repeatable coverage before using a held-out split."""

    base_counts = Counter(_base_cell(episode.stratum) for episode in episodes)
    missing = sorted(_EXPECTED_BASE_CELLS - base_counts.keys())
    if missing:
        raise ValueError(
            f"recovery data does not cover every actual progress/severity cell; missing {missing}"
        )
    sparse = sorted(cell for cell, count in base_counts.items() if count < 2)
    if sparse:
        raise ValueError(
            "recovery data needs at least two episodes in every actual "
            f"progress/severity cell; sparse {sparse}"
        )
    direction_counts = Counter(episode.stratum[2] for episode in episodes)
    if any(direction_counts[direction] < 2 for direction in (0, 1)):
        raise ValueError("recovery data needs at least two actual perturbations in each direction")


def split_episodes(
    episodes: tuple[_RecoveryEpisode, ...], fraction: float, seed: int
) -> tuple[tuple[_RecoveryEpisode, ...], tuple[_RecoveryEpisode, ...]]:
    """Split complete episodes while balancing actual incident strata."""

    request = _SplitRequest(episodes, fraction, seed)
    shuffled, context = _prepare_split(request)
    if context is None:
        return tuple(shuffled), ()
    groups = _episode_groups(shuffled)
    allocation = _validation_allocation(context, groups)
    validation = _select_validation(context, groups, allocation)
    validation_ids = {id(episode) for episode in validation}
    training = tuple(episode for episode in shuffled if id(episode) not in validation_ids)
    _require_split_coverage(training, validation)
    return training, validation


def _prepare_split(request: _SplitRequest) -> tuple[list[_RecoveryEpisode], _SplitContext | None]:
    shuffled = list(request.episodes)
    generator = random.Random(request.seed)
    generator.shuffle(shuffled)
    if len(shuffled) < 2 or request.fraction == 0.0:
        return shuffled, None
    count = min(len(shuffled) - 1, max(1, round(len(shuffled) * request.fraction)))
    return shuffled, _SplitContext(count, request.fraction, generator)


def _ordinal_bin(value: float, boundaries: tuple[float, float]) -> int:
    return int(value >= boundaries[0]) + int(value >= boundaries[1])


def _episode_groups(
    episodes: list[_RecoveryEpisode],
) -> dict[tuple[int, int], list[_RecoveryEpisode]]:
    groups: dict[tuple[int, int], list[_RecoveryEpisode]] = defaultdict(list)
    for episode in episodes:
        groups[_base_cell(episode.stratum)].append(episode)
    return dict(groups)


def _base_cell(stratum: _RecoveryStratum) -> tuple[int, int]:
    return stratum[0], stratum[1]


def _validation_allocation(
    context: _SplitContext,
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]],
) -> dict[tuple[int, int], int]:
    cells = list(groups)
    context.generator.shuffle(cells)
    chosen = _balanced_cells(groups, cells, min(context.count, len(cells)))
    allocation = {cell: int(cell in chosen) for cell in cells}
    state = _AllocationState(context, groups, cells, allocation)
    while sum(allocation.values()) < context.count:
        _allocate_validation_episode(state)
    return allocation


def _allocate_validation_episode(state: _AllocationState) -> None:
    eligible = [
        cell for cell in state.cells if state.allocation[cell] < len(state.groups[cell]) - 1
    ]
    if not eligible:
        raise ValueError("recovery split cannot preserve training coverage in every cell")
    cell = max(eligible, key=lambda item: _allocation_priority(state, item))
    state.allocation[cell] += 1


def _allocation_priority(state: _AllocationState, cell: tuple[int, int]) -> tuple[float, int]:
    gap = len(state.groups[cell]) * state.context.fraction - state.allocation[cell]
    return gap, -state.cells.index(cell)


def _balanced_cells(
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]],
    cells: list[tuple[int, int]],
    count: int,
) -> frozenset[tuple[int, int]]:
    if count == len(cells):
        return frozenset(cells)
    rank = {cell: index for index, cell in enumerate(cells)}
    selected = min(
        combinations(cells, count),
        key=lambda value: (
            _cell_selection_cost(value, groups),
            tuple(rank[item] for item in value),
        ),
    )
    return frozenset(selected)


def _cell_selection_cost(
    cells: tuple[tuple[int, int], ...],
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]],
) -> float:
    target = len(cells) / 3.0
    marginal = sum(
        (sum(cell[axis] == category for cell in cells) - target) ** 2
        for axis in (0, 1)
        for category in range(3)
    )
    directions = {episode.stratum[2] for cell in cells for episode in groups[cell]}
    return marginal + 1_000.0 * len({0, 1} - directions)


def _select_validation(
    context: _SplitContext,
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]],
    allocation: Mapping[tuple[int, int], int],
) -> tuple[_RecoveryEpisode, ...]:
    right_counts = _validation_right_counts(context, groups, allocation)
    cells = list(groups)
    context.generator.shuffle(cells)
    selected: list[_RecoveryEpisode] = []
    for cell in cells:
        selection = _CellDirectionSelection(groups[cell], allocation[cell], right_counts[cell])
        selected.extend(_select_from_cell(context, selection))
    return tuple(selected)


def _validation_right_counts(
    context: _SplitContext,
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]],
    allocation: Mapping[tuple[int, int], int],
) -> Mapping[tuple[int, int], int]:
    """Choose validation directions jointly so both splits retain both directions."""

    cells = _shuffled_cells(context, groups)
    states = _right_count_states(cells, groups, allocation)
    right = _balanced_right_count(context, groups, states)
    return _selected_right_counts(cells, states, right)


def _shuffled_cells(
    context: _SplitContext, groups: Mapping[tuple[int, int], list[_RecoveryEpisode]]
) -> list[tuple[int, int]]:
    cells = list(groups)
    context.generator.shuffle(cells)
    return cells


def _right_count_states(
    cells: list[tuple[int, int]],
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]],
    allocation: Mapping[tuple[int, int], int],
) -> dict[int, tuple[int, ...]]:
    states: dict[int, tuple[int, ...]] = {0: ()}
    for cell in cells:
        options = _right_count_options(groups[cell], allocation[cell])
        states = _extend_right_count_states(states, options)
    return states


def _extend_right_count_states(
    states: Mapping[int, tuple[int, ...]], options: tuple[int, ...]
) -> dict[int, tuple[int, ...]]:
    next_states: dict[int, tuple[int, ...]] = {}
    for total, choices in states.items():
        for option in options:
            next_states.setdefault(total + option, (*choices, option))
    return next_states


def _selected_right_counts(
    cells: list[tuple[int, int]], states: Mapping[int, tuple[int, ...]], right: int
) -> Mapping[tuple[int, int], int]:
    selected_counts = states.get(right)
    if selected_counts is None:
        _raise_direction_coverage_error()
    return dict(zip(cells, selected_counts, strict=True))


def _right_count_options(episodes: list[_RecoveryEpisode], count: int) -> tuple[int, ...]:
    left = sum(episode.stratum[2] == 0 for episode in episodes)
    right = len(episodes) - left
    minimum = max(0, count - left)
    maximum = min(count, right)
    return tuple(range(minimum, maximum + 1))


def _balanced_right_count(
    context: _SplitContext,
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]],
    states: Mapping[int, tuple[int, ...]],
) -> int:
    all_episodes = _all_recovery_episodes(groups)
    candidates = _eligible_right_counts(context, states, all_episodes)
    if not candidates:
        _raise_direction_coverage_error()
    target = _target_right(context.count, all_episodes)
    return min(candidates, key=lambda value: (abs(value - target), value))


def _all_recovery_episodes(
    groups: Mapping[tuple[int, int], list[_RecoveryEpisode]],
) -> tuple[_RecoveryEpisode, ...]:
    return tuple(episode for episodes in groups.values() for episode in episodes)


def _eligible_right_counts(
    context: _SplitContext,
    states: Mapping[int, tuple[int, ...]],
    episodes: tuple[_RecoveryEpisode, ...],
) -> list[int]:
    total_right = sum(episode.stratum[2] for episode in episodes)
    total_left = len(episodes) - total_right
    return [
        value
        for value in states
        if 1 <= value <= total_right - 1 and 1 <= context.count - value <= total_left - 1
    ]


def _raise_direction_coverage_error() -> NoReturn:
    raise ValueError(
        "recovery validation split cannot preserve both actual perturbation directions; "
        "record additional incidents in the underrepresented direction"
    )


def _select_from_cell(
    context: _SplitContext,
    selection: _CellDirectionSelection,
) -> tuple[_RecoveryEpisode, ...]:
    episodes, count, right_count = (
        selection.episodes,
        selection.count,
        selection.right_count,
    )
    left = [episode for episode in episodes if episode.stratum[2] == 0]
    right = [episode for episode in episodes if episode.stratum[2] == 1]
    context.generator.shuffle(left)
    context.generator.shuffle(right)
    return (*left[: count - right_count], *right[:right_count])


def _target_right(count: int, episodes: tuple[_RecoveryEpisode, ...]) -> int:
    proportional = round(count * sum(episode.stratum[2] for episode in episodes) / len(episodes))
    return min(count - 1, max(1, proportional))


def _require_split_coverage(
    training: tuple[_RecoveryEpisode, ...], validation: tuple[_RecoveryEpisode, ...]
) -> None:
    expected = ((0, {0, 1, 2}), (1, {0, 1, 2}), (2, {0, 1}))
    for name, episodes in (("training", training), ("validation", validation)):
        strata = tuple(episode.stratum for episode in episodes)
        if any({stratum[axis] for stratum in strata} != values for axis, values in expected):
            raise ValueError(
                f"recovery {name} split does not cover every progress, severity and direction bin"
            )


__all__ = ["recovery_stratum", "require_stratified_coverage", "split_episodes"]
