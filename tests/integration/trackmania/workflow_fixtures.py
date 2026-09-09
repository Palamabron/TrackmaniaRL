"""Real map assets and archives shared by game-free command integration tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import yaml

from tests.unit.trackmania._lidar_fixtures import _asset
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.project.scaffold_run_templates import _trackmania_config
from trackmaniarl.trackmania.actions import (
    build_brake_tap_action_table,
    continuous_control_to_discrete_indices_batch,
)
from trackmaniarl.trackmania.demonstrations import Demonstration
from trackmaniarl.trackmania.geometry import BoundaryGeometry

ACTION_IDS = (0, 1, 3, 36, 39, 72, 73, 75)


def base_config(directory: Path) -> dict[str, Any]:
    geometry_path = _asset(directory)
    config = yaml.safe_load(_trackmania_config())
    config["artifacts_dir"] = str(directory / "artifacts")
    environment = config["components"]["environment"]["kwargs"]["config"]
    environment.update(
        geometry_path=str(geometry_path),
        expected_map_uid="trackmaniarl-test",
        decision_interval_ms=10.0,
        demonstration_control_aggregation=False,
    )
    config["components"]["feature_pipeline"]["kwargs"]["config"] = {
        "geometry_path": str(geometry_path),
        "expected_map_uid": "trackmaniarl-test",
        "include_track_relative": True,
    }
    config["evaluation"]["maps"] = [
        {
            "id": "fixture-map",
            "map_path": str(directory / "trackmaniarl-test.Map.Gbx"),
            "geometry_path": str(geometry_path),
            "expected_map_uid": "trackmaniarl-test",
        }
    ]
    config["evaluation"]["trials_per_map"] = 1
    config["training"].update(max_episode_steps=160, batch_size=2, n_step=1)
    config["components"]["replay_store"]["kwargs"] = {"capacity": 16}
    return config


def demonstration(config: dict[str, Any]) -> Demonstration:
    geometry = BoundaryGeometry(config["evaluation"]["maps"][0]["geometry_path"])
    frames = np.zeros((151, 33), dtype=np.float32)
    frames[:, 3] = np.arange(1, 152, dtype=np.float32) * 10.0
    frames[:, 4] = np.linspace(0, 10, len(frames))
    frames[:, 7] = 10.0
    frames[:, 10] = 1.0
    frames[:, 14] = 1.0
    frames[:, 16] = 10.0
    frames[:, 18] = 2.0
    frames[:, 29] = 1.0
    controls = np.tile(np.asarray([1.0, 0.0, 0.0], dtype=np.float32), (150, 1))
    controls[20:30, 0] = 0.0
    controls[100:110, 2] = 1.0
    frames[100:, 7] = 0.5
    frames[100:, 16] = 0.5
    frames[:-1, 30] = controls[:, 2]
    frames[:-1, 31] = controls[:, 0]
    frames[-1, 2] = 1.0
    _, table = build_brake_tap_action_table()
    actions = continuous_control_to_discrete_indices_batch(controls, table)
    return Demonstration(
        geometry.map_uid,
        geometry.sha256,
        1,
        frames,
        actions,
        controls,
        1.51,
        decision_interval_ms=10.0,
    )


def bc_config(config: dict[str, Any]) -> dict[str, Any]:
    components = config["components"]
    components["feature_pipeline"]["kwargs"]["config"]["mask_current_control_inputs"] = True
    components["learner"] = {
        "class_path": "trackmaniarl.trackmania.imitation_learning:BehaviorCloningLearner",
        "kwargs": {"max_steps": 2, "validation_interval": 1},
    }
    components["model_factory"] = {
        "class_path": "trackmaniarl.trackmania.imitation_learning:LidarBehaviorCloningModelFactory",
        "kwargs": {
            "action_ids": list(ACTION_IDS),
            "encoder_hidden_dim": 8,
            "encoder_output_dim": 8,
        },
    }
    components["environment"]["kwargs"]["config"]["compact_action_ids"] = list(ACTION_IDS)
    return config


def save_config(directory: Path, config: dict[str, Any]) -> Path:
    path = directory / "run.yaml"
    path.write_text(RunSpec.model_validate(config).to_yaml(), encoding="utf-8")
    return path


class ReplayEnvironment:
    def __init__(self, demo: Demonstration) -> None:
        self.demo = demo
        self.step_index = 0
        self.actions: list[Any] = []
        self.closed = False

    def reset(self, *, seed: int | None = None) -> tuple[np.ndarray, dict[str, Any]]:
        self.step_index = 0
        return self.demo.frames[0].copy(), {}

    def step(self, action: Any) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        self.actions.append(action)
        self.step_index += 1
        frame = self.demo.frames[self.step_index].copy()
        finished = self.step_index == len(self.demo.actions)
        return (
            frame,
            1.0,
            finished,
            False,
            {
                "termination_reason": "finished" if finished else "",
                "race_time_ms": float(frame[3]),
                "progress_pct": self.step_index / 1.5,
            },
        )

    def close(self) -> None:
        self.closed = True
