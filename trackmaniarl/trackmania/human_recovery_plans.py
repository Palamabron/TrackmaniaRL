"""Seeded and coverage-balanced perturbation plans for recovery recording."""

from __future__ import annotations

import numpy as np

from trackmaniarl.trackmania.human_recovery_recording_types import (
    HumanRecoveryEpisodePlan,
    HumanRecoveryRecordingConfig,
)


def sample_human_recovery_plan(
    config: HumanRecoveryRecordingConfig, generator: np.random.Generator
) -> HumanRecoveryEpisodePlan:
    """Sample one reproducible plan inside the configured windows."""

    target = float(generator.uniform(config.target_progress_min, config.target_progress_max))
    duration = float(
        generator.uniform(
            config.perturbation_duration_min_ms,
            config.perturbation_duration_max_ms,
        )
    )
    direction = float(generator.choice(np.asarray([-1.0, 1.0], dtype=np.float32)))
    return _episode_plan(target, duration, direction)


def sample_human_recovery_plans(
    config: HumanRecoveryRecordingConfig, generator: np.random.Generator, count: int
) -> tuple[HumanRecoveryEpisodePlan, ...]:
    """Build a session balanced across progress, severity, and direction cells."""

    if count < 1:
        raise ValueError("recovery plan count must be positive")
    categories = _stratified_categories(count, generator)
    return tuple(_stratified_plan(config, generator, _category_tuple(row)) for row in categories)


def resample_human_recovery_plan(
    config: HumanRecoveryRecordingConfig,
    generator: np.random.Generator,
    template: HumanRecoveryEpisodePlan,
) -> HumanRecoveryEpisodePlan:
    """Resample inside a failed plan's coverage cell so retries can vary safely."""

    categories = (
        _category(_progress_edges(config), template.target_progress),
        _category(_duration_edges(config), template.perturbation_duration_ms),
        int(template.perturbation_control[2] > 0.0),
    )
    return _stratified_plan(config, generator, categories)


def _stratified_categories(count: int, generator: np.random.Generator) -> np.ndarray:
    cells = np.asarray(
        [
            (progress, duration, direction)
            for progress in range(3)
            for duration in range(3)
            for direction in range(2)
        ],
        dtype=np.int64,
    )
    complete, remainder = divmod(count, len(cells))
    parts = [np.tile(cells, (complete, 1))] if complete else []
    if remainder:
        parts.append(cells[generator.permutation(len(cells))[:remainder]])
    categories = np.concatenate(parts, axis=0)
    generator.shuffle(categories)
    return categories


def _stratified_plan(
    config: HumanRecoveryRecordingConfig,
    generator: np.random.Generator,
    categories: tuple[int, int, int],
) -> HumanRecoveryEpisodePlan:
    progress, duration, direction = categories
    target = _sample_bin(_progress_edges(config), progress, generator)
    duration_ms = _sample_bin(_duration_edges(config), duration, generator)
    return _episode_plan(target, duration_ms, (-1.0, 1.0)[direction])


def _progress_edges(config: HumanRecoveryRecordingConfig) -> np.ndarray:
    lower, upper = config.target_progress_min, config.target_progress_max
    span = upper - lower
    return np.asarray([lower, lower + span * 10 / 28, lower + span * 20 / 28, upper])


def _duration_edges(config: HumanRecoveryRecordingConfig) -> np.ndarray:
    bounds = (config.perturbation_duration_min_ms, config.perturbation_duration_max_ms)
    return np.linspace(bounds[0], bounds[1], 4, dtype=np.float64)


def _sample_bin(edges: np.ndarray, category: int, generator: np.random.Generator) -> float:
    return float(generator.uniform(edges[category], edges[category + 1]))


def _category(edges: np.ndarray, value: float) -> int:
    return min(int(np.searchsorted(edges[1:], value, side="right")), 2)


def _category_tuple(row: np.ndarray) -> tuple[int, int, int]:
    return int(row[0]), int(row[1]), int(row[2])


def _episode_plan(target: float, duration_ms: float, direction: float) -> HumanRecoveryEpisodePlan:
    control = np.asarray([1.0, 0.0, direction], dtype=np.float32)
    return HumanRecoveryEpisodePlan(target, duration_ms, control)
