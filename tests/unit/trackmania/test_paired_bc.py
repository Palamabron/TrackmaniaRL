from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import torch

from tests.integration.trackmania.test_vision_bc import _episode
from tests.unit.trackmania._lidar_fixtures import _asset
from trackmaniarl.trackmania.geometry import BoundaryGeometry
from trackmaniarl.trackmania.imitation_learning.data import horizontal_flip_observation
from trackmaniarl.trackmania.imitation_learning.vision import LidarVisionBehaviorCloningPipeline
from trackmaniarl.trackmania.imitation_learning.vision_data import (
    VisionLapLoadRequest,
    load_vision_behavior_cloning_laps,
    load_vision_demonstration,
    save_vision_demonstration,
)


def test_paired_bc_archive_alignment_and_control_masking(tmp_path: Path) -> None:
    geometry_path = _asset(tmp_path)
    geometry = BoundaryGeometry(geometry_path)
    pipeline = LidarVisionBehaviorCloningPipeline(
        {"geometry_path": geometry_path, "mask_current_control_inputs": True},
        {"width": 8, "height": 8},
    )
    paths = []
    for seed in range(3):
        demo = _episode(geometry, seed)
        telemetry = np.zeros((4, 33), dtype=np.float32)
        telemetry[:, 3] = demo.timestamps_ms
        telemetry[:, 12] = 1
        telemetry[:, 30:33] = 1
        demo = replace(demo, telemetry=telemetry)
        path = tmp_path / f"paired-{seed}.npz"
        save_vision_demonstration(path, demo)
        np.testing.assert_array_equal(load_vision_demonstration(path).telemetry, telemetry)
        paths.append(path)
    laps = load_vision_behavior_cloning_laps(
        VisionLapLoadRequest(paths, pipeline, (0, 36, 72), demo.contract)
    )
    assert not pipeline.images._frames
    for lap in laps:
        for observation in lap.observations:
            assert torch.count_nonzero(observation["telemetry"][17:20]) == 0
    for telemetry in (np.zeros((4, 32)), np.full((4, 33), np.nan), np.zeros((4, 33))):
        with pytest.raises(ValueError, match="telemetry"):
            replace(demo, telemetry=telemetry).validate()
    with pytest.raises(ValueError, match="target leakage"):
        LidarVisionBehaviorCloningPipeline({"geometry_path": geometry_path})


def test_paired_pipeline_rejects_image_only_episodes(tmp_path: Path) -> None:
    geometry_path = _asset(tmp_path)
    geometry = BoundaryGeometry(geometry_path)
    paths = []
    for seed in range(3):
        path = tmp_path / f"image-{seed}.npz"
        save_vision_demonstration(path, _episode(geometry, seed))
        paths.append(path)
    pipeline = LidarVisionBehaviorCloningPipeline(
        {"geometry_path": geometry_path, "mask_current_control_inputs": True}
    )
    with pytest.raises(ValueError, match="sensor modalities"):
        load_vision_behavior_cloning_laps(
            VisionLapLoadRequest(paths, pipeline, (0, 36, 72), _episode(geometry, 0).contract)
        )


def test_paired_reflection_changes_both_sensors_and_is_an_involution() -> None:
    observation = {
        "lidar": torch.randn(8, 12),
        "lidar_mask": torch.ones(12),
        "telemetry": torch.randn(46),
        "images": torch.rand(4, 8, 8),
    }
    reflected = horizontal_flip_observation(observation)
    assert not torch.equal(reflected["lidar"], observation["lidar"])
    torch.testing.assert_close(reflected["images"], observation["images"].flip(-1))
    twice = horizontal_flip_observation(reflected)
    for key in observation:
        torch.testing.assert_close(twice[key], observation[key])
