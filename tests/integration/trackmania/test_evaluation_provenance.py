"""Failures, timer sources and observed camera timing survive evaluation export."""

from __future__ import annotations

import json
from math import isfinite
from pathlib import Path
from typing import Any

import pytest

from tests.integration.trackmania.test_scaffold_evaluation import (
    _evaluation_suite,
    _EvaluationPolicy,
    _IdentityPipeline,
    _patch_geometry,
)
from trackmaniarl.core.contracts import EvaluatorRuntimeRequest
from trackmaniarl.core.environment_errors import EnvironmentPausedError
from trackmaniarl.trackmania.evaluation import TrackmaniaEvaluator


class _ScenarioEnvironment:
    def __init__(self, scenario: str, clock: object = 12345.0) -> None:
        self.scenario, self.clock, self.steps = scenario, clock, 0

    def reset(self, *, seed: int | None = None) -> tuple[float, dict[str, Any]]:
        self.steps = 0
        return 0.0, {}

    def step(self, action: Any) -> tuple[float, float, bool, bool, dict[str, Any]]:
        self.steps += 1
        if self.scenario == "telemetry_error" and self.steps == 2:
            raise TimeoutError("test packet deadline")
        if self.scenario == "capture_interruption" and self.steps == 2:
            raise EnvironmentPausedError("background")
        terminated = self.scenario in {"finished", "no_progress", "terminated"}
        truncated = self.scenario == "truncated"
        info = {
            "progress_pct": 23.0,
            "vision/capture_ms": 3.0,
            "vision/pairing_delay_ms": 4.0,
            "step_race_time_ms": 50.0,
        }
        if self.scenario in {"finished", "no_progress"}:
            info["termination_reason"] = self.scenario
        if self.scenario == "finished":
            info["race_time_ms"] = self.clock
        return 1.0, 2.0, terminated, truncated, info

    def close(self) -> None:
        pass


class _ScenarioFactory:
    def __init__(self, scenario: str, clock: object = 12345.0) -> None:
        self.scenario, self.clock = scenario, clock

    def create(self, *, seed: int, evaluation_map: object) -> _ScenarioEnvironment:
        return _ScenarioEnvironment(self.scenario, self.clock)


@pytest.mark.parametrize(
    "scenario",
    [
        "finished",
        "no_progress",
        "max_steps",
        "truncated",
        "terminated",
        "telemetry_error",
        "capture_interruption",
    ],
)
def test_every_declared_trial_retains_its_termination_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, scenario: str
) -> None:
    _patch_geometry(monkeypatch)
    evaluator = TrackmaniaEvaluator(
        EvaluatorRuntimeRequest(
            _evaluation_suite(tmp_path, trials_per_map=3),
            _ScenarioFactory(scenario),
            _IdentityPipeline(),
            max_episode_steps=2,
            run_dir=tmp_path,
        )
    )
    metrics = evaluator.evaluate(_EvaluationPolicy())
    trials = json.loads((tmp_path / "evaluation.json").read_text())["trials"]
    assert len(trials) == 3
    assert all(item["termination_reason"] == scenario for item in trials)
    assert metrics["eval/finish_rate"] == float(scenario == "finished")
    assert all(item["progress_pct"] == 23.0 for item in trials)
    assert metrics["eval/vision_capture_ms"] == 3.0
    assert metrics["eval/vision_pairing_delay_ms"] == 4.0
    assert metrics["eval/vision_pairing_delay_ms_p95_max"] == 4.0
    for item in trials:
        assert item["vision_capture_measurement_count"] == item["steps"]
        assert item["action_latency_ms_p95"] >= 0.0
        if scenario == "finished":
            assert item["finish_time_s"] == 12.345
            assert item["finish_time_source"] == "race_clock"
        else:
            assert item["finish_time_s"] is None
            assert item["finish_time_source"] is None
        if scenario == "telemetry_error":
            assert item["steps"] == 1
            assert "test packet deadline" in item["telemetry_error"]


@pytest.mark.parametrize("clock", [None, float("inf"), float("nan"), True, 0.0])
def test_finished_trial_marks_elapsed_fallback_when_race_clock_is_unusable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, clock: object
) -> None:
    _patch_geometry(monkeypatch)
    evaluator = TrackmaniaEvaluator(
        EvaluatorRuntimeRequest(
            _evaluation_suite(tmp_path),
            _ScenarioFactory("finished", clock),
            _IdentityPipeline(),
            run_dir=tmp_path,
        )
    )
    metrics = evaluator.evaluate(_EvaluationPolicy())
    assert all(isfinite(value) for value in metrics.values())
    trial = json.loads((tmp_path / "evaluation.json").read_text())["trials"][0]
    assert trial["finished"] is True
    assert trial["finish_time_source"] == "elapsed_fallback"
    assert trial["finish_time_s"] > 0


def test_evaluation_waits_for_visibility_before_reset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from types import SimpleNamespace

    waits = []

    class Environment:
        calls = 0

        def reset(self, *, seed: int) -> tuple[str, dict[str, Any]]:
            self.calls += 1
            if self.calls < 3:
                raise EnvironmentPausedError("background")
            return "ready", {}

    monkeypatch.setattr("trackmaniarl.trackmania.evaluation.sleep", waits.append)
    environment = Environment()
    evaluator = TrackmaniaEvaluator(
        EvaluatorRuntimeRequest(
            _evaluation_suite(tmp_path), _ScenarioFactory("finished"), _IdentityPipeline()
        )
    )
    result = evaluator._reset_available(SimpleNamespace(environment=environment, seed=0))
    assert result == ("ready", {})
    assert waits == [0.5, 0.5]
