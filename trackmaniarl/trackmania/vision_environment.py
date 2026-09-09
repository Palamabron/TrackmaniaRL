"""Synchronous screen capture paired with the Openplanet reward/control environment."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from trackmaniarl.core.contracts import FeaturePipeline
from trackmaniarl.core.data import Transition
from trackmaniarl.trackmania.environment import OpenPlanetEnvironmentFactory
from trackmaniarl.trackmania.environment_config import TrackmaniaEnvironmentConfig


class CaptureRegion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    left: int = 0
    top: int = 0
    width: int = Field(default=1280, ge=1)
    height: int = Field(default=720, ge=1)


class FrameSource(Protocol):
    def capture(self) -> np.ndarray[Any, Any]: ...

    def close(self) -> None: ...


class ScreenFrameSource:
    """Capture a configured desktop rectangle; the game must remain visible."""

    def __init__(self, region: CaptureRegion) -> None:
        try:
            import mss
        except ImportError as exc:
            raise ImportError("Live vision requires pip install 'trackmaniarl[vision]'") from exc
        self._screen = mss.mss()
        self._region = region.model_dump()

    def capture(self) -> np.ndarray[Any, Any]:
        bgra = np.asarray(self._screen.grab(self._region))
        return np.ascontiguousarray(bgra[:, :, 2::-1])

    def close(self) -> None:
        self._screen.close()


class VisionEnvironment:
    """Replace policy telemetry with RGB while retaining telemetry-based rewards."""

    def __init__(self, environment: Any, frames: FrameSource) -> None:
        self.environment = environment
        self.frames = frames

    def _capture(self, info: dict[str, Any]) -> np.ndarray[Any, Any]:
        started = perf_counter()
        frame = self.frames.capture()
        info["vision/capture_ms"] = (perf_counter() - started) * 1000.0
        return frame

    def reset(self, *, seed: int | None = None) -> tuple[np.ndarray[Any, Any], dict[str, Any]]:
        _, info = self.environment.reset(seed=seed)
        return self._capture(info), info

    def step(self, action: Any) -> tuple[np.ndarray[Any, Any], float, bool, bool, dict[str, Any]]:
        _, reward, terminated, truncated, info = self.environment.step(action)
        return self._capture(info), reward, terminated, truncated, info

    def close(self) -> None:
        try:
            self.environment.close()
        finally:
            self.frames.close()


class VisionEnvironmentFactory:
    def __init__(
        self,
        config: TrackmaniaEnvironmentConfig | dict[str, Any],
        *,
        capture: CaptureRegion | Mapping[str, Any] | None = None,
        base_dir: str | Path = ".",
    ) -> None:
        self._factory = OpenPlanetEnvironmentFactory(config, base_dir=base_dir)
        self.config = self._factory.config
        self.capture = CaptureRegion.model_validate({} if capture is None else capture)

    def create(self, *, seed: int, evaluation_map: Any | None = None) -> VisionEnvironment:
        frames = ScreenFrameSource(self.capture)
        try:
            environment = self._factory.create(seed=seed, evaluation_map=evaluation_map)
        except BaseException:
            frames.close()
            raise
        return VisionEnvironment(environment, frames)

    def load_demonstration(self, path: str | Path, pipeline: FeaturePipeline) -> list[Transition]:
        raise ValueError("Telemetry-only demonstrations have no RGB frames for vision training")
