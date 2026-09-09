from __future__ import annotations

from pathlib import Path

import pytest
import torch
import yaml

from trackmaniarl.core.builtins import TorchCheckpointCodec
from trackmaniarl.models.factory import CompositeValueModelFactory
from trackmaniarl.models.loading import WarmStartOptions, warm_start_composite_model
from trackmaniarl.project.scaffold_run_templates import (
    _trackmania_config,
    _trackmania_vision_config,
)
from trackmaniarl.trackmania.imitation_learning import (
    BehaviorCloningLearner,
    LidarBehaviorCloningModelFactory,
)
from trackmaniarl.trackmania.imitation_learning.vision import VisionBehaviorCloningModelFactory


@pytest.mark.parametrize("vision", [False, True])
def test_bc_encoder_warm_start_is_supported_and_failure_is_atomic(
    tmp_path: Path,
    *,
    vision: bool,
) -> None:
    factory = (
        VisionBehaviorCloningModelFactory((0, 36, 72))
        if vision
        else LidarBehaviorCloningModelFactory(action_ids=(0, 36, 72))
    )
    learner = BehaviorCloningLearner()
    learner.setup({"seed": 17, "model_factory": factory})
    checkpoint = tmp_path / "bc-policy.pt"
    TorchCheckpointCodec().save(
        {
            "schema_version": "trackmaniarl-bc-policy-v2",
            "learner": learner.state_dict(),
        },
        checkpoint,
    )
    config = yaml.safe_load(_trackmania_vision_config() if vision else _trackmania_config())
    model = CompositeValueModelFactory(**config["components"]["model_factory"]["kwargs"]).build()
    before = {name: tensor.clone() for name, tensor in model.state_dict().items()}
    with pytest.raises(ValueError, match="required tensors"):
        warm_start_composite_model(
            model, checkpoint, WarmStartOptions(required_tensors=("absent",))
        )
    for name, value in model.state_dict().items():
        torch.testing.assert_close(value, before[name], rtol=0, atol=0)
    report = warm_start_composite_model(model, checkpoint, WarmStartOptions())
    assert report.matched
    assert all(name.startswith(("encoder.", "temporal.")) for name in report.matched)
    source = learner.state_dict()["model"]
    for name in report.matched:
        torch.testing.assert_close(model.state_dict()[name], source[name], rtol=0, atol=0)
    for name, value in model.state_dict().items():
        if name.startswith(("head.", "strategy.")):
            torch.testing.assert_close(value, before[name], rtol=0, atol=0)
