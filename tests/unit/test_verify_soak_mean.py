from __future__ import annotations

import json
from pathlib import Path
from statistics import fmean, median

import pytest

from scripts import verify_soak
from tests.unit.test_verify_soak import (
    EvidenceBundleBuilder,
    ReportView,
    _json_object,
    _json_objects,
    _load_json,
)

_MIXED_RUNTIME_TIMINGS: tuple[dict[str, object], ...] = (
    {
        "steps": 1,
        "step_race_time_ms_max": 60.0,
        "step_race_time_measurement_count": 1,
        "step_race_time_measurements_valid": True,
    },
    {
        "steps": 2,
        "step_race_time_ms_max": 50.0,
        "step_race_time_measurement_count": 1,
        "step_race_time_measurements_valid": False,
    },
)


def _mean_gate_bundle(tmp_path: Path, times: list[float]) -> Path:
    run_dir = EvidenceBundleBuilder(tmp_path).build()
    _configure_suite(run_dir, len(times))
    _configure_trials(run_dir, times)
    return run_dir


def _configure_suite(run_dir: Path, trial_count: int) -> None:
    path = run_dir / "manifest.json"
    manifest = _load_json(path)
    config = _json_object(manifest["config"])
    suite = _json_object(config["evaluation"])
    suite["trials_per_map"] = trial_count
    suite["target_mean_s"] = 37.0
    path.write_text(json.dumps(manifest), encoding="utf-8")


def _configure_trials(run_dir: Path, times: list[float]) -> None:
    path = run_dir / "evaluation.json"
    evaluation = _load_json(path)
    template = _json_objects(evaluation["trials"])[0]
    evaluation["trials"] = [
        {**template, "trial_index": index, "finish_time_s": finish_time_s}
        for index, finish_time_s in enumerate(times)
    ]
    evaluation["metrics"] = {
        "eval/finish_rate": 1.0,
        "eval/median_finish_time_s": median(times),
        "eval/finish_time_s": fmean(times),
    }
    path.write_text(json.dumps(evaluation), encoding="utf-8")


def _runtime_gate_bundle(tmp_path: Path, maximum_ms: float | None) -> Path:
    run_dir = _mean_gate_bundle(tmp_path, [36.9])
    _enable_runtime_gate(run_dir)
    _set_runtime_trial_maximum(run_dir, maximum_ms)
    return run_dir


def _enable_runtime_gate(run_dir: Path) -> None:
    manifest_path = run_dir / "manifest.json"
    manifest = _load_json(manifest_path)
    suite = _json_object(_json_object(manifest["config"])["evaluation"])
    suite["max_step_race_time_ms"] = 100.0
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def _set_runtime_trial_maximum(run_dir: Path, maximum_ms: float | None) -> None:
    evaluation_path = run_dir / "evaluation.json"
    evaluation = _load_json(evaluation_path)
    trial = _json_objects(evaluation["trials"])[0]
    trial["steps"] = 1
    trial["step_race_time_measurement_count"] = 1
    trial["step_race_time_measurements_valid"] = True
    if maximum_ms is not None:
        trial["step_race_time_ms_max"] = maximum_ms
    evaluation_path.write_text(json.dumps(evaluation), encoding="utf-8")


def _mixed_runtime_gate_bundle(tmp_path: Path) -> Path:
    run_dir = _mean_gate_bundle(tmp_path, [36.8, 36.9])
    _enable_runtime_gate(run_dir)
    _set_mixed_runtime_trial_timing(run_dir)
    return run_dir


def _set_mixed_runtime_trial_timing(run_dir: Path) -> None:
    evaluation_path = run_dir / "evaluation.json"
    evaluation = _load_json(evaluation_path)
    trials = _json_objects(evaluation["trials"])
    for trial, timing in zip(trials, _MIXED_RUNTIME_TIMINGS, strict=False):
        trial.update(timing)
    evaluation_path.write_text(json.dumps(evaluation), encoding="utf-8")


@pytest.mark.parametrize(
    ("times", "expected_status"),
    [
        ([36.6] * 9 + [50.0], "failed"),
        ([37.0] * 10, "failed"),
        ([36.9] * 10, "passed"),
    ],
)
def test_soak_verification_enforces_strict_optional_mean_gate(
    tmp_path: Path, times: list[float], expected_status: str
) -> None:
    report = verify_soak.verify_run(_mean_gate_bundle(tmp_path, times))
    view = ReportView(report)
    assert report["status"] == expected_status
    assert view.check("final_benchmark_artifact") is (expected_status == "passed")
    assert view.section("benchmark")["mean_finish_time_s"] == pytest.approx(fmean(times))


@pytest.mark.parametrize(
    ("maximum_ms", "expected_status"),
    [(100.0, "passed"), (100.01, "failed"), (0.0, "failed"), (None, "failed")],
)
def test_soak_verification_enforces_optional_runtime_gate(
    tmp_path: Path, maximum_ms: float | None, expected_status: str
) -> None:
    report = verify_soak.verify_run(_runtime_gate_bundle(tmp_path, maximum_ms))
    view = ReportView(report)
    assert report["status"] == expected_status
    assert view.check("final_benchmark_artifact") is (expected_status == "passed")
    observed = view.section("benchmark")["max_step_race_time_ms"]
    assert observed == maximum_ms


def test_soak_runtime_gate_rejects_one_missing_step_hidden_by_a_positive_max(
    tmp_path: Path,
) -> None:
    report = verify_soak.verify_run(_mixed_runtime_gate_bundle(tmp_path))
    view = ReportView(report)
    assert report["status"] == "failed"
    assert view.check("final_benchmark_artifact") is False
    benchmark = view.section("benchmark")
    assert benchmark["max_step_race_time_ms"] == 60.0
    assert benchmark["step_race_time_measurements_valid"] is False
    assert benchmark["step_race_time_measurement_count"] == 2
    assert benchmark["step_race_time_expected_measurement_count"] == 3
