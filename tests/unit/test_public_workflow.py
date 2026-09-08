"""Public project and benchmark contracts that must work without local game assets."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import trackmaniarl
from trackmaniarl.commands.evaluation import _apply_benchmark_gate, _benchmark_spec
from trackmaniarl.commands.helpers import _training_learner_state
from trackmaniarl.commands.parser import build_parser
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.project.scaffold import create_project


def test_generated_own_map_project_and_recording_cli(tmp_path: Path) -> None:
    project = create_project(tmp_path / "agent", "agent", template="trackmania")
    config = project / "run.yaml"
    spec = RunSpec.from_yaml(config)
    assert trackmaniarl.RunSpec is RunSpec
    assert spec.evaluation is not None
    assert spec.evaluation.target_median_s is None
    assert "REPLACE_WITH_YOUR_MAP_UID" in config.read_text()
    args = build_parser().parse_args(
        [
            "benchmark",
            str(config),
            "policy.pt",
            "--record",
            "all.mkv",
            "--trials",
            "30",
        ]
    )
    first, suite = _benchmark_spec(args)
    second, _ = _benchmark_spec(args)
    assert first.run_id != second.run_id != spec.run_id
    assert suite.trials_per_map == 30
    assert args.record == Path("all.mkv")


def test_historical_full_benchmark_is_recomputed_without_filtering() -> None:
    source = Path(__file__).parents[2] / "docs/benchmarks/2026-09-08-v108-trials.json"
    data = json.loads(source.read_text())
    trials = data["trials"]
    times = [trial["finish_time_s"] for trial in trials]
    assert len(trials) == 30
    assert all(trial["finished"] for trial in trials)
    assert sum(times) == pytest.approx(1109.30)
    assert sum(times) / len(times) == pytest.approx(36.9766666667)
    assert max(times) == 41.37
    assert sum(trial["telemetry_skipped_frames_total"] for trial in trials) == 458


def test_benchmark_without_time_target_still_requires_finishes(tmp_path: Path) -> None:
    project = create_project(tmp_path / "agent", "agent", template="trackmania")
    suite = RunSpec.from_yaml(project / "run.yaml").evaluation
    assert suite is not None
    trial = {
        "finished": True,
        "finish_time_s": 150.0,
        "telemetry_error": None,
        "controller_error": None,
    }
    metrics = {"eval/median_finish_time_s": 150.0, "eval/finish_time_s": 150.0}
    _apply_benchmark_gate([trial], metrics, suite)
    with pytest.raises(RuntimeError, match="benchmark failed"):
        _apply_benchmark_gate([{**trial, "finished": False}], metrics, suite)


def test_training_checkpoint_does_not_accept_legacy_schema() -> None:
    with pytest.raises(ValueError, match="unsupported training checkpoint schema"):
        _training_learner_state({"schema_version": "1.0", "learner": {}})
    assert _training_learner_state({"schema_version": "2.0", "learner": {}}) == {}
