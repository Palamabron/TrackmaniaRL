from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch

from trackmaniarl.core.data import Transition
from trackmaniarl.experiments.graph_iqn_v2 import TrackGnnSimbaEncoderV2
from trackmaniarl.experiments.graph_iqn_v3 import (
    CONTEXT_V3_DIM,
    CONTEXT_V3_LAYOUT,
    AdapterOnlyDiscreteValueLearner,
    BoundaryGraphFeaturePipelineV3,
    TrackGnnSimbaEncoderV3,
)
from trackmaniarl.models.composite import CompositeValueModel
from trackmaniarl.models.factory import CompositeValueModelFactory
from trackmaniarl.trackmania.geometry import GEOMETRY_ASSET_VERSION


def _geometry(path: Path) -> Path:
    center = np.zeros((700, 3), dtype=np.float32)
    center[:, 0] = np.arange(700, dtype=np.float32)
    np.savez_compressed(
        path,
        version=np.array(GEOMETRY_ASSET_VERSION),
        map_uid=np.array("test-map"),
        map_sha256=np.array("test-map-hash"),
        left=center - np.array([0.0, 0.0, 2.0], dtype=np.float32),
        center=center,
        right=center + np.array([0.0, 0.0, 2.0], dtype=np.float32),
        spacing_m=np.array(1.0),
        recorded_count=np.array(600),
    )
    return path


def _frame(*, x: float = 100.0, z: float = 0.0, speed: float = 80.0) -> np.ndarray:
    values = np.zeros(33, dtype=np.float32)
    values[3], values[4], values[6] = 1_000.0, x, z
    values[7], values[10] = speed, 1.0
    values[16], values[17], values[18] = speed, 8_000.0, 4.0
    values[21], values[22], values[29] = 0.2, 0.3, 0.9
    values[31] = 1.0
    return values


def _named(context: torch.Tensor) -> dict[str, float]:
    return dict(zip(CONTEXT_V3_LAYOUT, context.tolist(), strict=True))


def _model(encoder: str) -> CompositeValueModel:
    return CompositeValueModelFactory(
        encoder={"class_path": encoder},
        temporal={
            "class_path": "trackmaniarl.models.temporal:IdentityTemporalCore",
            "kwargs": {"input_dim": 192},
        },
        head={"class_path": "trackmaniarl.experiments.graph_iqn:DuelingImplicitQuantileHead"},
        strategy={
            "class_path": "trackmaniarl.models.strategies:RandomQuantileStrategy",
            "kwargs": {"train_quantile_count": 64, "target_quantile_count": 64},
        },
    ).build()


def _encoder_observation() -> dict[str, torch.Tensor]:
    return {
        "physics": torch.randn(3, 60),
        "track": torch.randn(3, 3, 88),
        "context": torch.randn(3, CONTEXT_V3_DIM),
    }


@pytest.fixture
def pipeline(tmp_path: Path) -> BoundaryGraphFeaturePipelineV3:
    return BoundaryGraphFeaturePipelineV3(_geometry(tmp_path / "g.npz"), "test-map")


def test_v3_context_shape_and_vehicle_features(pipeline: BoundaryGraphFeaturePipelineV3) -> None:
    prepared = pipeline.transform_observation(_frame())
    context = _named(prepared["context"])

    assert prepared["physics"].shape == (60,)
    assert prepared["track"].shape == (3, 88)
    assert prepared["context"].shape == (CONTEXT_V3_DIM,)
    assert context["signed_lateral_offset"] == pytest.approx(0.0)
    assert context["left_clearance"] == pytest.approx(1.0)
    assert context["right_clearance"] == pytest.approx(1.0)
    assert context["rear_left_slip"] == pytest.approx(0.2)
    assert context["rear_right_slip"] == pytest.approx(0.3)
    assert context["rpm"] == pytest.approx(0.8)
    assert context["adherence"] == pytest.approx(0.9)
    assert torch.isfinite(prepared["context"]).all()


def test_v3_signed_offset_and_clearance(pipeline: BoundaryGraphFeaturePipelineV3) -> None:
    context = _named(pipeline.transform_observation(_frame(z=1.0))["context"])

    assert context["signed_lateral_offset"] == pytest.approx(0.5)
    assert context["left_clearance"] == pytest.approx(1.5)
    assert context["right_clearance"] == pytest.approx(0.5)
    assert context["minimum_clearance"] == pytest.approx(0.5)


def test_v3_prepared_observation_validation(pipeline: BoundaryGraphFeaturePipelineV3) -> None:
    prepared: dict[str, Any] = {
        "physics": np.zeros(60, dtype=np.float32),
        "track": np.zeros((3, 88), dtype=np.float32),
        "context": np.zeros(CONTEXT_V3_DIM, dtype=np.float32),
    }

    transformed = pipeline.transform_observation(prepared)
    assert transformed["context"].shape == (CONTEXT_V3_DIM,)

    with pytest.raises(ValueError, match="requires physics, track and context"):
        pipeline.transform_observation({"physics": prepared["physics"], "track": prepared["track"]})


def test_v3_collates_replay_observations(pipeline: BoundaryGraphFeaturePipelineV3) -> None:
    observation = pipeline.transform_observation(_frame())
    batch = pipeline.collate(
        [
            Transition(
                observation=observation,
                action=0,
                reward=0.0,
                next_observation=observation,
                terminated=False,
                truncated=False,
                info={},
            )
        ]
    )

    assert batch["observations"]["context"].shape == (1, CONTEXT_V3_DIM)


def test_v3_encoder_is_exact_v2_policy_at_initialization() -> None:
    torch.manual_seed(7)
    v2 = TrackGnnSimbaEncoderV2().eval()
    v3 = TrackGnnSimbaEncoderV3().eval()
    missing, unexpected = v3.load_state_dict(v2.state_dict(), strict=False)
    observation = _encoder_observation()

    assert missing
    assert all(name.startswith("context_adapter.") for name in missing)
    assert unexpected == []
    baseline = v2({"physics": observation["physics"], "track": observation["track"]})
    torch.testing.assert_close(v3(observation), baseline, rtol=0.0, atol=0.0)


def test_v3_encoder_context_branch_can_learn() -> None:
    encoder = TrackGnnSimbaEncoderV3()
    observation = {
        "physics": torch.randn(2, 60),
        "track": torch.randn(2, 3, 88),
        "context": torch.randn(2, CONTEXT_V3_DIM),
    }

    encoder(observation).sum().backward()

    assert encoder.context_adapter[-1].weight.grad is not None
    assert torch.count_nonzero(encoder.context_adapter[-1].weight.grad) > 0


def test_v3_encoder_hard_bounds_context_correction() -> None:
    scale = 0.02
    encoder = TrackGnnSimbaEncoderV3(context_residual_scale=scale)
    with torch.no_grad():
        encoder.context_adapter[-1].weight.fill_(100.0)
        encoder.context_adapter[-1].bias.fill_(100.0)

    correction = encoder._context_correction(torch.randn(4, CONTEXT_V3_DIM))

    assert correction.abs().max() <= scale
    assert correction.abs().max().item() == pytest.approx(scale)


@pytest.mark.parametrize("scale", [0.0, -0.1, 1.01, float("inf")])
def test_v3_encoder_rejects_invalid_context_scale(scale: float) -> None:
    with pytest.raises(ValueError, match="context_residual_scale"):
        TrackGnnSimbaEncoderV3(context_residual_scale=scale)


def test_adapter_only_learner_only_optimizes_context_adapter() -> None:
    model = _model("trackmaniarl.experiments.graph_iqn_v3:TrackGnnSimbaEncoderV3")
    learner = AdapterOnlyDiscreteValueLearner(model=model)
    learner.setup({"seed": 0, "run_dir": None, "model_factory": None})

    trainable = {name for name, parameter in model.named_parameters() if parameter.requires_grad}
    assert trainable
    assert all(name.startswith("encoder.context_adapter.") for name in trainable)
