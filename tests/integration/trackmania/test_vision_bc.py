from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch
import yaml

from tests.integration.trackmania.workflow_fixtures import base_config, save_config
from trackmaniarl.cli import entrypoint
from trackmaniarl.core.builtins import TorchCheckpointCodec
from trackmaniarl.core.runtime import resolve_run
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.project.scaffold_run_templates import _trackmania_bc_vision_config
from trackmaniarl.trackmania.geometry import BoundaryGeometry
from trackmaniarl.trackmania.imitation_learning import RecoveryContract
from trackmaniarl.trackmania.imitation_learning.vision import VisionBehaviorCloningPipeline
from trackmaniarl.trackmania.imitation_learning.vision_data import (
    VisionDemonstration,
    VisionLapLoadRequest,
    load_vision_behavior_cloning_laps,
    load_vision_demonstration,
    save_vision_demonstration,
)
from trackmaniarl.trackmania.vision_environment import VisionEnvironmentFactory


def _config(tmp_path: Path, *, previous_action: bool) -> dict[str, Any]:
    base = base_config(tmp_path)
    config = yaml.safe_load(_trackmania_bc_vision_config())
    config["artifacts_dir"] = str(tmp_path / "artifacts")
    config["evaluation"] = base["evaluation"]
    components = config["components"]
    components["environment"]["kwargs"]["config"] = base["components"]["environment"]["kwargs"][
        "config"
    ]
    components["environment"]["kwargs"]["config"]["compact_action_ids"] = [0, 36, 72]
    components["model_factory"]["kwargs"].update(
        action_ids=[0, 36, 72],
        config={"hidden_dim": 8, "previous_action_conditioning": previous_action},
    )
    components["feature_pipeline"]["kwargs"] = {"config": {"width": 8, "height": 8}}
    components["learner"]["kwargs"].update(max_steps=2, validation_interval=1)
    config["training"].update(batch_size=2, max_episode_steps=4)
    return config


def _episode(geometry: BoundaryGeometry, seed: int) -> VisionDemonstration:
    return VisionDemonstration(
        np.random.default_rng(seed).integers(0, 256, (4, 8, 8, 3), dtype=np.uint8),
        np.array([0, 36, 72, 36]),
        np.array([0.0, 10.0, 20.0, 30.0]),
        RecoveryContract(geometry.map_uid, geometry.sha256, 1, 10.0, "frame_start"),
        0.04,
    )


class _ImageRollout:
    def __init__(self) -> None:
        self.steps = 0
        self.closed = False

    def reset(self, *, seed: int | None = None) -> tuple[Any, dict[str, Any]]:
        self.steps = 0
        return np.zeros((8, 8, 3), dtype=np.uint8), {}

    def step(self, action: int) -> tuple[Any, float, bool, bool, dict[str, Any]]:
        assert 0 <= action < 3
        self.steps += 1
        return (
            np.full((8, 8, 3), self.steps, dtype=np.uint8),
            1.0,
            self.steps == 4,
            False,
            {
                "termination_reason": "finished" if self.steps == 4 else "",
                "race_time_ms": self.steps * 10.0,
                "progress_pct": self.steps * 25.0,
            },
        )

    def close(self) -> None:
        self.closed = True


@pytest.mark.parametrize("previous_action", [False, True])
def test_camera_bc_cli_train_resume_and_benchmark(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    previous_action: bool,
) -> None:
    config = _config(tmp_path, previous_action=previous_action)
    path = save_config(tmp_path, config)
    geometry = BoundaryGeometry(config["evaluation"]["maps"][0]["geometry_path"])
    demos = tmp_path / "demos"
    demos.mkdir()
    for index in range(3):
        save_vision_demonstration(demos / f"{index}.npz", _episode(geometry, index))
    entrypoint(["validate", str(path)])
    run = resolve_run(RunSpec.from_yaml(path), base_dir=tmp_path)
    try:
        run.learner.setup({"seed": 0, "model_factory": run.model_factory})
        initial = run.learner.model.encoder.convolution[0].weight.detach().clone()
    finally:
        run.logger.close()
    original_save = TorchCheckpointCodec.save

    def save_with_midrun_snapshot(self: Any, state: Any, target: Any) -> None:
        original_save(self, state, target)
        if (
            state.get("schema_version") == "trackmaniarl-bc-training-v2"
            and state["training"]["step"] == 1
        ):
            original_save(self, state, Path(target).with_name("midrun.pt"))

    monkeypatch.setattr(TorchCheckpointCodec, "save", save_with_midrun_snapshot)
    entrypoint(["bc-train", str(path), "--demo", str(demos), "--horizontal-flip-augmentation"])
    checkpoint = next((tmp_path / "artifacts").rglob("bc-latest.pt"))
    state = TorchCheckpointCodec().load(checkpoint)
    assert state["training"]["step"] == 2
    assert not torch.equal(initial, state["learner"]["model"]["encoder.convolution.0.weight"])
    manifest = json.loads((checkpoint.parent.parent / "bc-dataset-manifest.json").read_text())
    training = {source.split("#")[0] for source in manifest["training_sources"]}
    assert training.isdisjoint(manifest["validation_sources"])
    entrypoint(
        [
            "bc-train",
            str(path),
            "--demo",
            str(demos),
            "--horizontal-flip-augmentation",
            "--resume",
            str(checkpoint.with_name("midrun.pt")),
        ]
    )
    restored = TorchCheckpointCodec().load(checkpoint)
    for key, value in state["learner"]["model"].items():
        torch.testing.assert_close(value, restored["learner"]["model"][key], rtol=0, atol=0)
    environment = _ImageRollout()
    monkeypatch.setattr(VisionEnvironmentFactory, "create", lambda *a, **kw: environment)
    selected = checkpoint.with_name("bc-best-validation.pt")
    entrypoint(["bc-benchmark", str(path), str(selected), "--trials", "2", "--report-only"])
    assert environment.closed


def test_vision_archives_validate_contracts_and_reset_stacks(tmp_path: Path) -> None:
    config = _config(tmp_path, previous_action=False)
    geometry = BoundaryGeometry(config["evaluation"]["maps"][0]["geometry_path"])
    paths = []
    for index in range(3):
        path = tmp_path / f"{index}.npz"
        save_vision_demonstration(path, _episode(geometry, index))
        paths.append(path)
    pipeline = VisionBehaviorCloningPipeline({"width": 8, "height": 8})
    request = VisionLapLoadRequest(paths, pipeline, (0, 36, 72), _episode(geometry, 0).contract)
    laps = load_vision_behavior_cloning_laps(request)
    for lap in laps:
        image = lap.observations[0]["images"]
        torch.testing.assert_close(image[0], image[-1])
        assert lap.labels.tolist() == [0, 1, 2, 1]
    with pytest.raises(FileExistsError):
        save_vision_demonstration(paths[0], _episode(geometry, 0))
    duplicate = tmp_path / "duplicate.npz"
    save_vision_demonstration(duplicate, load_vision_demonstration(paths[0]))
    with pytest.raises(ValueError, match="duplicate"):
        load_vision_behavior_cloning_laps(
            VisionLapLoadRequest(
                [*paths, duplicate],
                pipeline,
                (0, 36, 72),
                request.contract,
            )
        )
    wrong = RecoveryContract("other-map", geometry.sha256, 1, 10.0, "frame_start")
    with pytest.raises(ValueError, match="contract"):
        load_vision_behavior_cloning_laps(VisionLapLoadRequest(paths, pipeline, (0, 36, 72), wrong))
    with pytest.raises(ValueError, match="compact"):
        load_vision_behavior_cloning_laps(
            VisionLapLoadRequest(paths, pipeline, (0,), request.contract)
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("frames", np.zeros((4, 8, 8, 3), dtype=np.float32)),
        ("actions", np.array([0, 36, 72])),
        ("actions", np.array([0, 36, 72, 78])),
        ("actions", np.array([0.0, 36.0, 72.0, 36.0])),
        ("timestamps_ms", np.array([0.0, 10.0, 10.0, 30.0])),
        ("timestamps_ms", np.array([0.0, 10.0, float("nan"), 30.0])),
        ("finish_time_s", float("inf")),
        ("finish_time_s", 0.03),
    ],
)
def test_vision_archive_rejects_invalid_data(tmp_path: Path, field: str, value: Any) -> None:
    contract = RecoveryContract("map", "a" * 64, 1, 10.0, "frame_start")
    demonstration = VisionDemonstration(
        np.zeros((4, 8, 8, 3), dtype=np.uint8),
        np.array([0, 36, 72, 36]),
        np.array([0.0, 10.0, 20.0, 30.0]),
        contract,
        0.04,
    )
    with pytest.raises(ValueError, match="vision demo"):
        save_vision_demonstration(
            tmp_path / "invalid.npz", replace(demonstration, **{field: value})
        )
    assert not (tmp_path / "invalid.npz").exists()
