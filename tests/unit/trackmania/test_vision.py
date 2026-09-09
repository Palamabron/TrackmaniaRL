from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest
import torch

from trackmaniarl.core.data import Transition
from trackmaniarl.trackmania.vision import VisionFeaturePipeline
from trackmaniarl.trackmania.vision_environment import (
    CaptureRegion,
    ScreenFrameSource,
    VisionEnvironment,
    VisionEnvironmentFactory,
)
from trackmaniarl.trackmania.vision_models import VisionSensorEncoder


def test_vision_resizes_normalizes_and_clears_episode_history() -> None:
    pipeline = VisionFeaturePipeline({"width": 8, "height": 12, "frame_stack": 2})
    dark = np.zeros((20, 30, 3), dtype=np.uint8)
    light = np.full_like(dark, 255)
    first = pipeline.transform_observation(dark)
    second = pipeline.transform_observation(light)
    assert first.shape == (2, 12, 8)
    assert first.dtype == torch.float32
    assert torch.count_nonzero(first) == 0
    torch.testing.assert_close(second[0], torch.zeros(12, 8))
    torch.testing.assert_close(second[1], torch.ones(12, 8))
    pipeline.reset_episode()
    torch.testing.assert_close(pipeline.transform_observation(light), torch.ones(2, 12, 8))


def test_rgb_channel_order_and_collation_do_not_change_history() -> None:
    pipeline = VisionFeaturePipeline({"width": 8, "height": 8, "grayscale": False})
    rgb = np.zeros((8, 8, 3), dtype=np.uint8)
    rgb[:, :, 0] = 255
    prepared = pipeline.transform_observation(rgb)
    before = tuple(pipeline._frames)
    transition = Transition(prepared, np.zeros(3), 1.0, prepared, False, True)
    batch = pipeline.collate([transition, transition])
    assert batch["observations"].shape == (2, 12, 8, 8)
    assert tuple(pipeline._frames) == before
    torch.testing.assert_close(prepared[0], torch.ones(8, 8))
    assert torch.count_nonzero(prepared[1:3]) == 0
    with pytest.raises(ValueError, match="shape"):
        pipeline.collate([Transition(torch.zeros(3), 0, 0.0, prepared, False, False)])


@pytest.mark.parametrize(("shape", "dtype"), [((8, 8, 4), np.uint8), ((8, 8, 3), np.float32)])
def test_vision_rejects_ambiguous_raw_image_contract(shape: tuple[int, ...], dtype: Any) -> None:
    with pytest.raises(ValueError, match="uint8 RGB"):
        VisionFeaturePipeline().transform_observation(np.zeros(shape, dtype=dtype))


def test_vision_encoder_preserves_batch_time_axes_and_gradients() -> None:
    encoder = VisionSensorEncoder(channels=4, output_dim=8, hidden_dim=8)
    images = torch.rand(2, 3, 4, 8, 8)
    features = encoder(images)
    assert features.shape == (2, 3, 8)
    features.sum().backward()
    assert encoder.convolution[0].weight.grad is not None
    with pytest.raises(ValueError, match="shape"):
        encoder(torch.zeros(2, 3, 8, 8))


class _Frames:
    def __init__(self) -> None:
        self.count = 0
        self.closed = False

    def capture(self) -> np.ndarray[Any, Any]:
        self.count += 1
        return np.full((8, 8, 3), self.count, dtype=np.uint8)

    def close(self) -> None:
        self.closed = True


class _Environment:
    def reset(self, *, seed: int | None = None) -> tuple[None, dict[str, Any]]:
        return None, {"seed": seed}

    def step(self, action: Any) -> tuple[None, float, bool, bool, dict[str, Any]]:
        return None, 2.0, True, False, {"action": action, "termination_reason": "finished"}

    def close(self) -> None:
        raise RuntimeError("close failed")


def test_vision_environment_preserves_control_rewards_and_closes_camera_on_error() -> None:
    frames = _Frames()
    environment = VisionEnvironment(_Environment(), frames)
    first, info = environment.reset(seed=9)
    assert info["seed"] == 9
    assert np.all(first == 1)
    image, reward, terminated, truncated, info = environment.step(7)
    assert np.all(image == 2)
    assert (reward, terminated, truncated) == (2.0, True, False)
    assert info["action"] == 7
    assert info["vision/capture_ms"] >= 0
    with pytest.raises(RuntimeError, match="close failed"):
        environment.close()
    assert frames.closed


def test_screen_source_converts_bgra_and_uses_requested_region(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    regions: list[dict[str, int]] = []

    def grab(region: dict[str, int]) -> np.ndarray[Any, Any]:
        regions.append(region)
        return np.array([[[10, 20, 30, 255]]], dtype=np.uint8)

    screen = SimpleNamespace(grab=grab, close=lambda: None)
    monkeypatch.setitem(sys.modules, "mss", SimpleNamespace(mss=lambda: screen))
    region = CaptureRegion(left=-100, top=4, width=1, height=1)
    source = ScreenFrameSource(region)
    assert source.capture().tolist() == [[[30, 20, 10]]]
    assert regions == [region.model_dump()]
    source.close()


def test_camera_resources_close_when_game_initialization_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frames = _Frames()
    monkeypatch.setattr(
        "trackmaniarl.trackmania.vision_environment.ScreenFrameSource", lambda region: frames
    )
    factory = VisionEnvironmentFactory({"geometry_path": "missing.npz"})

    def fail_create(**kwargs: Any) -> Any:
        raise FileNotFoundError("missing geometry")

    monkeypatch.setattr(factory._factory, "create", fail_create)
    with pytest.raises(FileNotFoundError):
        factory.create(seed=0)
    assert frames.closed
