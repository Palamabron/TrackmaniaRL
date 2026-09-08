from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

from trackmaniarl.core.contracts import PolicyMode
from trackmaniarl.trackmania import human_recovery_data
from trackmaniarl.trackmania.human_recovery import (
    HumanRecoveryEpisodePlan,
    HumanRecoveryRecordingConfig,
    HumanRecoveryRecordingRequest,
    RecoveryAttemptError,
    load_recovery_demonstration,
    record_human_recovery_episode,
    sample_human_recovery_plan,
    save_recovery_demonstration,
)
from trackmaniarl.trackmania.human_recovery_plans import resample_human_recovery_plan
from trackmaniarl.trackmania.human_recovery_recording import sample_human_recovery_plans
from trackmaniarl.trackmania.telemetry import TelemetryFrame


class _Pipeline:
    def __init__(self) -> None:
        self.reset_count = 0

    def reset_episode(self) -> None:
        self.reset_count += 1

    def transform_observation(self, observation: Any) -> np.ndarray:
        return np.asarray(observation, dtype=np.float32)

    def collate(self, transitions: list[Any]) -> list[Any]:
        return transitions


class _Policy:
    def __init__(self) -> None:
        self.calls = 0
        self.reset_count = 0

    def reset_episode(self) -> None:
        self.reset_count += 1

    def act(self, observation: Any, mode: PolicyMode = PolicyMode.ONLINE) -> int:
        del observation
        assert mode is PolicyMode.EVALUATION
        self.calls += 1
        return 0


class _Controller:
    def __init__(self) -> None:
        self.applied: list[np.ndarray] = []

    def apply(self, control: np.ndarray) -> None:
        self.applied.append(np.asarray(control, dtype=np.float32).copy())


class _Client:
    def __init__(self, frames: list[np.ndarray]) -> None:
        self.frames = list(frames)

    def read_next(self) -> TelemetryFrame:
        if not self.frames:
            raise TimeoutError("test telemetry exhausted")
        return TelemetryFrame(self.frames.pop(0))


class _Environment:
    def __init__(self) -> None:
        self.config = _environment_config()
        self.geometry = SimpleNamespace(map_uid="test-map", sha256="a" * 64)
        self.controller = _Controller()
        self._model_frames = [
            (_frame(1_000.0, control=(1.0, 0.0)), 30.0),
            (_frame(2_100.0, control=(1.0, 0.0)), 61.0),
        ]
        self.client = _Client(_post_target_frames())

    def reset(self, *, seed: int | None = None) -> tuple[np.ndarray, dict[str, Any]]:
        assert seed == 0
        return _frame(100.0), {}

    def step(self, action: Any) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        assert action == 0
        frame, progress = self._model_frames.pop(0)
        return frame, 0.0, False, False, {"progress_pct": progress}


def _environment_config() -> SimpleNamespace:
    return SimpleNamespace(
        action_repeat_frames=1,
        decision_interval_ms=50.0,
        position_indices=(4, 5, 6),
        velocity_indices=(7, 8, 9),
        velocity_to_mps_scale=1.0,
    )


def _post_target_frames() -> list[np.ndarray]:
    return [
        _frame(2_150.0, control=(1.0, 1.0)),
        _frame(2_200.0, control=(1.0, 1.0)),
        _frame(2_250.0, control=(1.0, 1.0)),
        _frame(2_300.0),
        _frame(2_350.0),
        _frame(2_400.0, control=(1.0, -1.0)),
        _frame(2_450.0, control=(1.0, -0.5)),
        _frame(2_500.0, control=(1.0, 0.0), finish_value=1.0),
    ]


def _frame(
    race_time_ms: float,
    control: tuple[float, float] = (0.0, 0.0),
    finish_value: float = 0.0,
) -> np.ndarray:
    frame = np.zeros(33, dtype=np.float32)
    frame[2] = finish_value
    frame[3] = race_time_ms
    frame[4] = race_time_ms / 100.0
    frame[7] = 10.0
    frame[10] = 1.0
    frame[16] = 10.0
    frame[30] = control[1]
    frame[31] = control[0]
    return frame


def _request(environment: _Environment) -> HumanRecoveryRecordingRequest:
    return HumanRecoveryRecordingRequest(
        environment=environment,
        policy=_Policy(),
        feature_pipeline=_Pipeline(),
        checkpoint_sha256="b" * 64,
        status=lambda _message: None,
    )


def test_human_recovery_aligns_delayed_takeover_and_preserves_full_context() -> None:
    environment = _Environment()
    for frame, steer in zip(environment.client.frames[:3], (0.8, 0.9, 1.0), strict=True):
        frame[30] = steer
    request = _request(environment)
    plan = HumanRecoveryEpisodePlan(0.60, 150.0, np.asarray([1.0, 0.0, 1.0]))

    recovery = record_human_recovery_episode(request, plan)

    _assert_observed_perturbation(recovery, plan, environment)
    _assert_takeover_alignment(recovery)
    assert recovery.demonstration.finish_time_s == pytest.approx(2.5)


def _assert_observed_perturbation(recovery: Any, plan: Any, environment: Any) -> None:
    assert recovery.perturbation_start_step == 3
    assert recovery.perturbation_steps == 3
    assert recovery.takeover_step == 8
    assert recovery.takeover_step > recovery.perturbation_start_step + recovery.perturbation_steps
    assert len(recovery.demonstration.actions[recovery.takeover_step :]) == 2
    assert recovery.actual_progress == pytest.approx(0.61)
    assert recovery.actual_perturbation_duration_ms == pytest.approx(150.0)
    np.testing.assert_allclose(recovery.perturbation_control, [1.0, 0.0, 0.9])
    assert not np.array_equal(recovery.perturbation_control, plan.perturbation_control)
    assert np.array_equal(environment.controller.applied[0], plan.perturbation_control)
    assert np.array_equal(environment.controller.applied[-1], np.zeros(3, dtype=np.float32))


def _assert_takeover_alignment(recovery: Any) -> None:
    controls = recovery.demonstration.controls
    assert np.array_equal(controls[recovery.takeover_step - 1], np.zeros(3, dtype=np.float32))
    expected = np.asarray([1.0, 0.0, -1.0], dtype=np.float32)
    assert np.array_equal(controls[recovery.takeover_step], expected)


def test_human_recovery_archive_round_trip(tmp_path: Path) -> None:
    recovery = record_human_recovery_episode(
        _request(_Environment()),
        HumanRecoveryEpisodePlan(0.60, 150.0, np.asarray([1.0, 0.0, 1.0])),
    )

    path = save_recovery_demonstration(tmp_path / "recovery", recovery)
    loaded = load_recovery_demonstration(path)

    assert loaded.perturbation_start_step == recovery.perturbation_start_step
    assert loaded.perturbation_steps == recovery.perturbation_steps
    assert loaded.takeover_step == recovery.takeover_step
    assert loaded.target_progress == recovery.target_progress
    assert loaded.source_checkpoint_sha256 == "b" * 64
    assert np.array_equal(loaded.demonstration.frames, recovery.demonstration.frames)
    assert np.array_equal(loaded.demonstration.actions, recovery.demonstration.actions)
    assert not any(path.name.endswith(".tmp.npz") for path in tmp_path.iterdir())


def _fail_after_partial_write(path: Path, **_values: Any) -> None:
    Path(path).write_bytes(b"partial archive")
    raise OSError("simulated write failure")


def test_human_recovery_archive_write_failure_preserves_target_and_cleans_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    recovery = record_human_recovery_episode(
        _request(_Environment()),
        HumanRecoveryEpisodePlan(0.60, 150.0, np.asarray([1.0, 0.0, 1.0])),
    )
    target = tmp_path / "recovery.npz"
    target.write_bytes(b"existing archive")

    monkeypatch.setattr(human_recovery_data.np, "savez_compressed", _fail_after_partial_write)
    with pytest.raises(OSError, match="simulated write failure"):
        save_recovery_demonstration(target, recovery)

    assert target.read_bytes() == b"existing archive"
    assert not any(path.name.endswith(".tmp.npz") for path in tmp_path.iterdir())


def test_human_recovery_archive_rejects_perturbation_metadata_outside_observed_controls() -> None:
    recovery = record_human_recovery_episode(
        _request(_Environment()),
        HumanRecoveryEpisodePlan(0.60, 150.0, np.asarray([1.0, 0.0, 1.0])),
    )

    with pytest.raises(ValueError, match="does not match observed controls"):
        replace(recovery, perturbation_start_step=recovery.perturbation_start_step - 1)


def test_recovery_plan_is_seeded_and_stays_inside_target_windows() -> None:
    config = HumanRecoveryRecordingConfig()
    first = sample_human_recovery_plan(config, np.random.default_rng(17))
    second = sample_human_recovery_plan(config, np.random.default_rng(17))

    assert first.target_progress == second.target_progress
    assert first.perturbation_duration_ms == second.perturbation_duration_ms
    assert np.array_equal(first.perturbation_control, second.perturbation_control)
    assert 0.55 <= first.target_progress <= 0.83
    assert 50.0 <= first.perturbation_duration_ms <= 200.0


def test_recovery_session_plan_balances_every_incident_cell() -> None:
    plans = sample_human_recovery_plans(
        HumanRecoveryRecordingConfig(), np.random.default_rng(17), 36
    )

    cells = Counter(_plan_cell(plan) for plan in plans)

    assert len(cells) == 18
    assert set(cells.values()) == {2}


def _plan_cell(plan: HumanRecoveryEpisodePlan) -> tuple[int, int, int]:
    progress = 0 if plan.target_progress < 0.65 else int(plan.target_progress >= 0.75) + 1
    duration = 0 if plan.perturbation_duration_ms < 100.0 else 1
    duration += int(plan.perturbation_duration_ms >= 150.0)
    direction = int(plan.perturbation_control[2] > 0.0)
    return progress, duration, direction


def test_failed_plan_resampling_preserves_its_coverage_cell() -> None:
    config = HumanRecoveryRecordingConfig()
    generator = np.random.default_rng(17)
    template = sample_human_recovery_plans(config, generator, 36)[0]

    retries = [resample_human_recovery_plan(config, generator, template) for _ in range(5)]

    assert all(_plan_cell(retry) == _plan_cell(template) for retry in retries)
    assert any(retry.target_progress != template.target_progress for retry in retries)


def test_perturbation_opposes_existing_non_neutral_model_steering() -> None:
    environment = _Environment()
    environment._model_frames[-1] = (_frame(2_100.0, control=(1.0, 0.6)), 61.0)
    for frame in environment.client.frames[:3]:
        frame[30] = -1.0

    recovery = record_human_recovery_episode(
        _request(environment),
        HumanRecoveryEpisodePlan(0.60, 150.0, np.asarray([1.0, 0.0, 1.0])),
    )

    assert recovery.perturbation_control[2] == pytest.approx(-1.0)
    assert environment.controller.applied[0][2] == pytest.approx(-1.0)


def test_unobserved_perturbation_discards_recovery_attempt() -> None:
    environment = _Environment()
    for frame in environment.client.frames[:3]:
        frame[30] = -1.0

    with pytest.raises(RecoveryAttemptError, match="did not confirm"):
        record_human_recovery_episode(
            _request(environment),
            HumanRecoveryEpisodePlan(0.60, 150.0, np.asarray([1.0, 0.0, 1.0])),
        )


def test_too_short_observed_perturbation_discards_recovery_attempt() -> None:
    environment = _Environment()
    environment.client.frames[1][30] = 0.0
    environment.client.frames[2][30] = 0.0

    with pytest.raises(RecoveryAttemptError, match="confirmed only 50 ms"):
        record_human_recovery_episode(
            _request(environment),
            HumanRecoveryEpisodePlan(0.60, 200.0, np.asarray([1.0, 0.0, 1.0])),
        )


def test_increasing_timer_teleport_discards_recovery_attempt() -> None:
    environment = _Environment()
    environment.client.frames[0][4] = 500.0

    with pytest.raises(RecoveryAttemptError, match="respawn or teleport"):
        record_human_recovery_episode(
            _request(environment),
            HumanRecoveryEpisodePlan(0.60, 150.0, np.asarray([1.0, 0.0, 1.0])),
        )


def _assert_recovery_parser_defaults(args: Any) -> None:
    assert args.count == 36
    assert args.target_progress_min == pytest.approx(0.55)
    assert args.target_progress_max == pytest.approx(0.83)
    assert args.perturbation_duration_min_ms == pytest.approx(50.0)
    assert args.perturbation_duration_max_ms == pytest.approx(200.0)
    assert args.takeover_timeout == pytest.approx(10.0)
    assert args.human_input_deadzone == pytest.approx(0.10)
