"""Trackmania adapter contracts and action encodings."""

from trackmaniarl.core.collector import CollectionResult, Environment, EpisodeCollector
from trackmaniarl.trackmania.actions import build_brake_tap_action_table
from trackmaniarl.trackmania.actor_critic import (
    TelemetryDiscreteSacModelFactory,
    TelemetryRedqModelFactory,
    TelemetrySacModelFactory,
)
from trackmaniarl.trackmania.assets import record_boundary, record_trajectory
from trackmaniarl.trackmania.baseline import TelemetryPpoModelFactory, TelemetryTqcModelFactory
from trackmaniarl.trackmania.encoders import LidarSensorEncoder
from trackmaniarl.trackmania.environment import (
    OpenPlanetEnvironmentFactory,
    TrackmaniaEnvironmentConfig,
)
from trackmaniarl.trackmania.evaluation import TrackmaniaEvaluator
from trackmaniarl.trackmania.features import LidarFeaturePipeline, TelemetryFeaturePipeline
from trackmaniarl.trackmania.vision import VisionConfig, VisionFeaturePipeline
from trackmaniarl.trackmania.vision_environment import (
    CaptureRegion,
    FrameSource,
    VisionEnvironment,
    VisionEnvironmentFactory,
)
from trackmaniarl.trackmania.vision_models import VisionPpoModelFactory, VisionSensorEncoder

__all__ = [
    "CaptureRegion",
    "CollectionResult",
    "Environment",
    "EpisodeCollector",
    "FrameSource",
    "LidarFeaturePipeline",
    "LidarSensorEncoder",
    "OpenPlanetEnvironmentFactory",
    "TelemetryDiscreteSacModelFactory",
    "TelemetryFeaturePipeline",
    "TelemetryPpoModelFactory",
    "TelemetryRedqModelFactory",
    "TelemetrySacModelFactory",
    "TelemetryTqcModelFactory",
    "TrackmaniaEnvironmentConfig",
    "TrackmaniaEvaluator",
    "VisionConfig",
    "VisionEnvironment",
    "VisionEnvironmentFactory",
    "VisionFeaturePipeline",
    "VisionPpoModelFactory",
    "VisionSensorEncoder",
    "build_brake_tap_action_table",
    "record_boundary",
    "record_trajectory",
]
