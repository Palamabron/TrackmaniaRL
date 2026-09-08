from __future__ import annotations

import pytest
import torch

from trackmaniarl.experiments.graph_iqn_v3 import CONTEXT_V3_DIM
from trackmaniarl.experiments.graph_iqn_v4 import (
    OrderedTrackResidualAdapter,
    SpatialAdapterOnlyDiscreteValueLearner,
    TrackGnnSimbaEncoderV4,
)
from trackmaniarl.models.composite import CompositeValueModel
from trackmaniarl.models.factory import CompositeValueModelFactory


def _observation(batch_size: int = 3) -> dict[str, torch.Tensor]:
    return {
        "physics": torch.randn(batch_size, 60),
        "track": torch.randn(batch_size, 3, 88),
        "context": torch.randn(batch_size, CONTEXT_V3_DIM),
    }


def _model() -> CompositeValueModel:
    return CompositeValueModelFactory(
        encoder={"class_path": "trackmaniarl.experiments.graph_iqn_v4:TrackGnnSimbaEncoderV4"},
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


def test_ordered_adapter_is_initially_inert_and_direction_sensitive_after_enable() -> None:
    torch.manual_seed(11)
    adapter = OrderedTrackResidualAdapter().eval()
    track = torch.randn(2, 3, 88)
    reversed_track = track.reshape(2, 3, 44, 2).flip(2).reshape(2, 3, 88)

    with torch.inference_mode():
        torch.testing.assert_close(adapter(track), torch.zeros(2, 192), rtol=0.0, atol=0.0)
        adapter.output_projection.weight.normal_()
        forward = adapter(track)
        backward = adapter(reversed_track)

    assert (forward - backward).abs().max() > 1.0e-4


def test_v4_spatial_correction_is_hard_bounded() -> None:
    scale = 0.02
    encoder = TrackGnnSimbaEncoderV4(spatial_residual_scale=scale)
    with torch.no_grad():
        encoder.spatial_adapter.output_projection.weight.fill_(100.0)
        encoder.spatial_adapter.output_projection.bias.fill_(100.0)

    correction = encoder._spatial_correction(torch.randn(4, 3, 88))

    assert correction.abs().max() <= scale
    assert correction.abs().max().item() == pytest.approx(scale)


@pytest.mark.parametrize("scale", [0.0, -0.1, 1.01, float("inf")])
def test_v4_rejects_invalid_spatial_scale(scale: float) -> None:
    with pytest.raises(ValueError, match="spatial_residual_scale"):
        TrackGnnSimbaEncoderV4(spatial_residual_scale=scale)


def test_spatial_adapter_only_learner_freezes_every_other_parameter() -> None:
    model = _model()
    learner = SpatialAdapterOnlyDiscreteValueLearner(model=model)
    learner.setup({"seed": 0, "run_dir": None, "model_factory": None})

    trainable = {name for name, parameter in model.named_parameters() if parameter.requires_grad}
    assert trainable
    assert all(name.startswith("encoder.spatial_adapter.") for name in trainable)
