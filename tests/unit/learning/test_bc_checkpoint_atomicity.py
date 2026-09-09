from __future__ import annotations

import random
from copy import deepcopy

import numpy as np
import pytest
import torch

from trackmaniarl.trackmania.imitation_learning import BehaviorCloningLearner
from trackmaniarl.trackmania.imitation_learning.vision import VisionBehaviorCloningModelFactory


@pytest.mark.parametrize(
    "failure", ["model", "optimizer", "rng", "nonfinite-model", "nonfinite-optimizer"]
)
def test_failed_bc_restore_preserves_every_component(failure: str) -> None:
    learner = BehaviorCloningLearner()
    learner.setup(
        {"model_factory": VisionBehaviorCloningModelFactory((0, 36, 72), {"hidden_dim": 8})}
    )
    learner.train_batch({"images": torch.rand(2, 4, 8, 8)}, torch.tensor([0, 1]), torch.ones(3))
    before = deepcopy(learner.state_dict())
    broken = deepcopy(before)
    for value in broken["model"].values():
        value.add_(1)
    if failure == "model":
        broken["model"].pop("head.bias")
    elif failure == "optimizer":
        broken["optimizer"]["param_groups"][0]["params"] = []
    elif failure == "nonfinite-model":
        broken["model"]["head.bias"].fill_(float("inf"))
    elif failure == "nonfinite-optimizer":
        next(iter(broken["optimizer"]["state"].values()))["exp_avg"].fill_(float("nan"))
    else:
        broken["rng"]["python"] = random.Random(123).getstate()
        broken["rng"]["torch"] = torch.zeros(1, dtype=torch.uint8)
    with pytest.raises(
        (RuntimeError, ValueError), match=r"Missing key|parameter group|RNG state|non-finite"
    ):
        learner.load_state_dict(broken)
    after = learner.state_dict()
    for component in ("model", "optimizer"):
        torch.testing.assert_close(after[component], before[component], rtol=0, atol=0)
    for component in ("scheduler", "scaler"):
        assert after[component] == before[component]
    assert after["rng"]["python"] == before["rng"]["python"]
    np.testing.assert_equal(after["rng"]["numpy"], before["rng"]["numpy"])
    torch.testing.assert_close(after["rng"]["torch"], before["rng"]["torch"], rtol=0, atol=0)
