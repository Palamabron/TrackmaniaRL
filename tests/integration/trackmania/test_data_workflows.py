from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from tests.integration.trackmania.workflow_fixtures import (
    ReplayEnvironment,
    base_config,
    bc_config,
    demonstration,
    save_config,
)
from trackmaniarl.cli import entrypoint
from trackmaniarl.core.builtins import TorchCheckpointCodec
from trackmaniarl.core.runtime import resolve_run
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.trackmania.demonstrations import save_demonstration
from trackmaniarl.trackmania.environment import OpenPlanetEnvironmentFactory
from trackmaniarl.trackmania.trajectory_optimization import TrajectorySchedule


@pytest.mark.parametrize("teacher_probability", [0, 1])
def test_dagger_routes_actions_resets_episodes_and_trains_bc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, teacher_probability: int
) -> None:
    config = bc_config(base_config(tmp_path))
    config_path = save_config(tmp_path, config)
    demo = demonstration(config)
    demos = tmp_path / "demonstrations"
    paths = [save_demonstration(demos / f"lap-{index}.npz", demo) for index in range(3)]
    source = tmp_path / "student.pt"
    run = resolve_run(RunSpec.from_yaml(config_path))
    try:
        run.learner.setup({"seed": 0, "model_factory": run.model_factory})
        run.checkpoint_codec.save(
            {"schema_version": "trackmaniarl-bc-policy-v2", "learner": run.learner.state_dict()},
            source,
        )
    finally:
        run.logger.close()
    environment = ReplayEnvironment(demo)
    monkeypatch.setattr(OpenPlanetEnvironmentFactory, "create", lambda *a, **kw: environment)
    output = tmp_path / "dagger.npz"
    entrypoint(
        [
            "dagger-collect",
            str(config_path),
            str(source),
            str(paths[0]),
            str(output),
            "--episodes",
            "3",
            "--teacher-probability",
            str(teacher_probability),
            "--intervention-error",
            "1000000",
        ]
    )
    assert environment.closed
    with np.load(output, allow_pickle=False) as archive:
        assert len(archive["frames"]) == 450
        assert np.flatnonzero(archive["episode_starts"]).tolist() == [0, 150, 300]
        assert np.all(archive["intervention"] == bool(teacher_probability))
        if teacher_probability == 0:
            np.testing.assert_array_equal(environment.actions, archive["student_action"])
        else:
            assert all(np.asarray(action).shape == (3,) for action in environment.actions)
        for start in (150, 300):
            np.testing.assert_array_equal(archive["frames"][0], archive["frames"][start])
    entrypoint(["bc-train", str(config_path), "--demo", str(demos), "--recovery", str(output)])
    latest = list((tmp_path / "artifacts").rglob("bc-latest.pt"))
    assert len(latest) == 1
    assert TorchCheckpointCodec().load(latest[0])["training"]["step"] == 2
    manifest = json.loads((latest[0].parent.parent / "bc-dataset-manifest.json").read_text())
    assert str(output.resolve()) in {item["path"] for item in manifest["files"]}
    assert set(manifest["training_sources"]).isdisjoint(manifest["validation_sources"])


def test_synthetic_recovery_command_produces_bc_training_data(tmp_path: Path) -> None:
    config = bc_config(base_config(tmp_path))
    config_path = save_config(tmp_path, config)
    demo = demonstration(config)
    demos = tmp_path / "demonstrations"
    paths = [save_demonstration(demos / f"lap-{index}.npz", demo) for index in range(3)]
    output = tmp_path / "synthetic.npz"
    entrypoint(
        [
            "trajectory-synthetic-recovery",
            str(config_path),
            str(paths[0]),
            str(output),
            "--sample-stride",
            "25",
        ]
    )
    original = output.read_bytes()
    with pytest.raises(ValueError, match="finite and positive"):
        entrypoint(
            [
                "trajectory-synthetic-recovery",
                str(config_path),
                str(paths[0]),
                str(output),
                "--sample-stride",
                "0",
            ]
        )
    assert output.read_bytes() == original
    entrypoint(["bc-train", str(config_path), "--demo", str(demos), "--recovery", str(output)])
    assert len(list((tmp_path / "artifacts").rglob("bc-best-validation.pt"))) == 1


def test_trajectory_command_persists_resumes_and_reports_unmet_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = base_config(tmp_path)
    config_path = save_config(tmp_path, config)
    demo = demonstration(config)
    source = save_demonstration(tmp_path / "demo.npz", demo)
    environments: list[ReplayEnvironment] = []

    def create(*args: Any, **kwargs: Any) -> ReplayEnvironment:
        environment = ReplayEnvironment(demo)
        environments.append(environment)
        return environment

    monkeypatch.setattr(OpenPlanetEnvironmentFactory, "create", create)
    output = tmp_path / "schedule.npz"
    arguments = [
        "trajectory-optimize",
        str(config_path),
        str(source),
        str(output),
        "--max-trials",
        "3",
        "--baseline-trials",
        "1",
        "--confirmation-trials",
        "1",
    ]
    entrypoint([*arguments, "--target-time", "2"])
    initial = TrajectorySchedule.load(output)
    with pytest.raises(RuntimeError, match="target not reached"):
        entrypoint([*arguments, "--target-time", "1"])
    restored = TrajectorySchedule.load(output)
    np.testing.assert_array_equal(initial.materialize(), restored.materialize())
    assert len(environments) == 2
    assert all(environment.closed for environment in environments)
    assert len(environments[1].actions) > len(demo.actions)
