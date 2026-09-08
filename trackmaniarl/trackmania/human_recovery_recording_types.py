"""Contracts and private state for live human-recovery recording."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from trackmaniarl.core.contracts import FeaturePipeline, Policy

StatusReporter = Callable[[str], None]


class RecoveryAttemptError(RuntimeError):
    """The current lap cannot provide a valid completed human-recovery example."""


@dataclass(frozen=True, slots=True)
class HumanRecoveryRecordingConfig:
    target_progress_min: float = 0.55
    target_progress_max: float = 0.83
    perturbation_duration_min_ms: float = 50.0
    perturbation_duration_max_ms: float = 200.0
    max_duration_s: float = 180.0
    minimum_context_s: float = 1.0
    takeover_timeout_s: float = 10.0
    human_input_deadzone: float = 0.10

    def __post_init__(self) -> None:
        _validate_recording_config(self)


@dataclass(frozen=True, slots=True)
class HumanRecoveryEpisodePlan:
    target_progress: float
    perturbation_duration_ms: float
    perturbation_control: np.ndarray

    def __post_init__(self) -> None:
        _validate_episode_plan(self)


@dataclass(frozen=True, slots=True)
class HumanRecoveryRecordingRequest:
    environment: Any
    policy: Policy
    feature_pipeline: FeaturePipeline
    checkpoint_sha256: str
    config: HumanRecoveryRecordingConfig = field(default_factory=HumanRecoveryRecordingConfig)
    status: StatusReporter = print


@dataclass(slots=True)
class CaptureState:
    current: np.ndarray
    frames: list[np.ndarray]
    actions: list[int]
    controls: list[np.ndarray]
    action_table: list[np.ndarray]
    deadline: float


@dataclass(frozen=True, slots=True)
class PerturbationResult:
    start_step: int
    steps: int
    takeover_step: int
    actual_duration_ms: float
    actual_control: np.ndarray


@dataclass(frozen=True, slots=True)
class PerturbationTiming:
    started_ms: float
    duration_ms: float
    control: np.ndarray


@dataclass(frozen=True, slots=True)
class PerturbationCapture:
    start_step: int
    steps: int
    actual_duration_ms: float
    actual_control: np.ndarray


@dataclass(frozen=True, slots=True)
class RecordedRecovery:
    state: CaptureState
    actual_progress: float
    perturbation: PerturbationResult


@dataclass(frozen=True, slots=True)
class PolicyStep:
    following: np.ndarray
    progress: float
    ended: bool
    reason: str


def _validate_recording_config(config: HumanRecoveryRecordingConfig) -> None:
    progress = (config.target_progress_min, config.target_progress_max)
    durations = (config.perturbation_duration_min_ms, config.perturbation_duration_max_ms)
    if not 0.0 < progress[0] <= progress[1] < 1.0:
        raise ValueError("recovery progress window must be ordered and inside (0, 1)")
    if not 0.0 < durations[0] <= durations[1] <= 1_000.0:
        raise ValueError("recovery perturbation window must be ordered inside (0, 1000] ms")
    _validate_recording_timing(config)


def _validate_recording_timing(config: HumanRecoveryRecordingConfig) -> None:
    timing = np.asarray(
        [config.max_duration_s, config.takeover_timeout_s, config.minimum_context_s]
    )
    if not np.isfinite(timing).all() or np.any(timing[:2] <= 0.0):
        raise ValueError("recovery lap and takeover timeouts must be positive")
    if config.minimum_context_s < 0.95:
        raise ValueError("recovery collection must preserve about one second of context")
    if not 0.0 < config.human_input_deadzone < 1.0:
        raise ValueError("human input deadzone must be inside (0, 1)")


def _validate_episode_plan(plan: HumanRecoveryEpisodePlan) -> None:
    if not 0.0 < plan.target_progress < 1.0:
        raise ValueError("recovery target progress must be inside (0, 1)")
    if not np.isfinite(plan.perturbation_duration_ms) or plan.perturbation_duration_ms <= 0:
        raise ValueError("recovery perturbation duration must be finite and positive")
    _validate_perturbation_control(plan.perturbation_control)


def _validate_perturbation_control(raw_control: np.ndarray) -> None:
    control = np.asarray(raw_control)
    if control.shape != (3,) or not np.allclose(control[:2], [1.0, 0.0]):
        raise ValueError("recovery perturbation must use full gas without braking")
    if not np.isclose(abs(float(control[2])), 1.0):
        raise ValueError("recovery perturbation must use full left or right steering")
