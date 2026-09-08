from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch

from trackmaniarl.experiments.graph_iqn_v3 import CONTEXT_V3_DIM, TrackGnnSimbaEncoderV3
from trackmaniarl.experiments.graph_iqn_v5 import (
    RECOVERY_V5_DIM,
    RECOVERY_V5_LAYOUT,
    BoundaryGraphFeaturePipelineV5,
    RecoveryTemporalOnlyDiscreteValueLearner,
    TrackGnnSimbaEncoderV5,
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


def _frame(time_ms: float, position: tuple[float, float], speed: float) -> np.ndarray:
    values = np.zeros(33, dtype=np.float32)
    x, z = position
    values[3], values[4], values[6] = time_ms, x, z
    values[7], values[10] = speed, 1.0
    values[16], values[17], values[18] = speed, 8_000.0, 4.0
    values[29], values[31] = 0.9, 1.0
    return values


def _observation(batch_size: int = 3) -> dict[str, torch.Tensor]:
    return {
        "physics": torch.randn(batch_size, 60),
        "track": torch.randn(batch_size, 3, 88),
        "context": torch.randn(batch_size, CONTEXT_V3_DIM),
        "recovery": torch.randn(batch_size, RECOVERY_V5_DIM),
    }


def _model() -> CompositeValueModel:
    return CompositeValueModelFactory(
        encoder={"class_path": "trackmaniarl.experiments.graph_iqn_v5:TrackGnnSimbaEncoderV5"},
        temporal={
            "class_path": "trackmaniarl.models.temporal:ZeroGatedResidualGruTemporalCore",
            "kwargs": {"input_dim": 192, "hidden_dim": 96, "residual_scale": 0.02},
        },
        head={"class_path": "trackmaniarl.experiments.graph_iqn:DuelingImplicitQuantileHead"},
        strategy={
            "class_path": "trackmaniarl.models.strategies:RandomQuantileStrategy",
            "kwargs": {"train_quantile_count": 64, "target_quantile_count": 64},
        },
    ).build()


@pytest.fixture
def pipeline(tmp_path: Path) -> BoundaryGraphFeaturePipelineV5:
    return BoundaryGraphFeaturePipelineV5(_geometry(tmp_path / "g.npz"), "test-map")


def test_v5_recovery_detects_speed_loss_and_edge_approach(
    pipeline: BoundaryGraphFeaturePipelineV5,
) -> None:
    first = pipeline.transform_observation(_frame(1_000, (100, 0), 80))
    second = pipeline.transform_observation(_frame(1_050, (103, 1), 60))
    named = dict(zip(RECOVERY_V5_LAYOUT, second["recovery"].tolist(), strict=True))

    torch.testing.assert_close(first["recovery"], torch.zeros(RECOVERY_V5_DIM))
    assert named["decision_interval_error"] == pytest.approx(0.0)
    assert named["speed_loss"] == pytest.approx(1.0)
    assert named["forward_speed_loss"] == pytest.approx(1.0)
    assert named["progress_advance"] > 0.0
    assert named["clearance_loss"] > 0.0
    assert named["edge_approach"] > 0.0
    assert named["retained_speed_deficit"] > 0.0
    assert named["recovery_memory"] > 0.0


def test_v5_reset_clears_temporal_recovery_state(pipeline: BoundaryGraphFeaturePipelineV5) -> None:
    pipeline.transform_observation(_frame(1_000, (100, 0), 80))
    pipeline.transform_observation(_frame(1_050, (102, 1), 50))
    pipeline.reset_episode()

    reset = pipeline.transform_observation(_frame(0, (0, 0), 0))

    torch.testing.assert_close(reset["recovery"], torch.zeros(RECOVERY_V5_DIM))


def test_v5_prepared_observation_validation(pipeline: BoundaryGraphFeaturePipelineV5) -> None:
    prepared: dict[str, Any] = {
        "physics": np.zeros(60, dtype=np.float32),
        "track": np.zeros((3, 88), dtype=np.float32),
        "context": np.zeros(CONTEXT_V3_DIM, dtype=np.float32),
        "recovery": np.zeros(RECOVERY_V5_DIM, dtype=np.float32),
    }
    assert pipeline.transform_observation(prepared)["recovery"].shape == (RECOVERY_V5_DIM,)

    prepared.pop("recovery")
    with pytest.raises(ValueError, match="requires physics, track, context and recovery"):
        pipeline.transform_observation(prepared)


def test_v5_is_exact_v3_policy_at_initialization() -> None:
    torch.manual_seed(12)
    v3 = TrackGnnSimbaEncoderV3(context_residual_scale=0.02).eval()
    v5 = TrackGnnSimbaEncoderV5(
        context_residual_scale=0.02,
        spatial_residual_scale=0.02,
        recovery_residual_scale=0.02,
    ).eval()
    missing, unexpected = v5.load_state_dict(v3.state_dict(), strict=False)
    observation = _observation()

    assert missing
    assert all(name.startswith(("spatial_adapter.", "recovery_adapter.")) for name in missing)
    assert unexpected == []
    baseline = v3({name: observation[name] for name in ("physics", "track", "context")})
    torch.testing.assert_close(v5(observation), baseline, rtol=0.0, atol=0.0)


def test_recovery_temporal_learner_freezes_source_policy() -> None:
    model = _model()
    learner = RecoveryTemporalOnlyDiscreteValueLearner(model=model, burn_in=2)
    learner.setup({"seed": 0, "run_dir": None, "model_factory": None})

    trainable = {name for name, parameter in model.named_parameters() if parameter.requires_grad}
    assert trainable
    assert all(name.startswith(("encoder.recovery_adapter.", "temporal.")) for name in trainable)
