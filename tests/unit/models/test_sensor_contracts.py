from __future__ import annotations

import pytest
import torch
from torch import nn

from trackmaniarl.models.actors import (
    CategoricalActor,
    GaussianActor,
    GaussianActorConfig,
    PpoGaussianActor,
)
from trackmaniarl.models.critics import ContinuousQCritic
from trackmaniarl.models.sensor_actor_critic import SensorActorCriticModelFactory
from trackmaniarl.trackmania.encoders import LidarSensorEncoder


@pytest.mark.parametrize("actor_type", [GaussianActor, PpoGaussianActor, CategoricalActor])
def test_actor_and_critic_accept_the_same_lidar_encoder(actor_type: type[nn.Module]) -> None:
    encoder = LidarSensorEncoder({"telemetry_dim": 6, "hidden_dim": 8, "output_dim": 8})
    observation = {
        "lidar": torch.rand(2, 4, 12),
        "lidar_mask": torch.ones(2, 12),
        "telemetry": torch.rand(2, 6),
    }
    actor = (
        actor_type(encoder, 8, 3)
        if actor_type is CategoricalActor
        else actor_type(encoder, GaussianActorConfig(8, 3))
    )
    actions, log_probability = actor(observation)
    assert torch.isfinite(actions).all()
    assert torch.isfinite(log_probability).all()
    critic = ContinuousQCritic(encoder, 8, 3)
    assert critic(observation, torch.zeros(2, 3)).shape == (2,)
    log_probability.sum().backward()
    assert any(p.grad is not None for p in encoder.parameters())


@pytest.mark.parametrize(
    ("low", "high"),
    [
        ([float("nan")], [1.0]),
        ([-1.0], [float("inf")]),
        ([-float("inf")], [1.0]),
        ([1.0], [1.0]),
        ([2.0], [1.0]),
        ([-3e38], [3e38]),
        ([2e38], [3e38]),
        ([], []),
    ],
)
@pytest.mark.parametrize("actor_type", [GaussianActor, PpoGaussianActor])
def test_actors_reject_unusable_action_bounds(
    low: list[float], high: list[float], actor_type: type[GaussianActor]
) -> None:
    with pytest.raises(ValueError, match="action bounds"):
        actor_type(nn.Identity(), GaussianActorConfig(2, len(low), low, high))


def test_ppo_accepts_an_encoder_with_biasless_linear_layers() -> None:
    actor = PpoGaussianActor(nn.Linear(2, 4, bias=False), GaussianActorConfig(4, 1))
    assert torch.isfinite(actor(torch.zeros(3, 2))[0]).all()


def test_sensor_factory_constructs_independent_encoders_and_checks_width() -> None:
    encoder = {
        "class_path": "trackmaniarl.trackmania.multimodal:BatchedLidarSensorEncoder",
        "kwargs": {"config": {"output_dim": 8, "hidden_dim": 8}},
    }
    model = SensorActorCriticModelFactory("sac", encoder, {"feature_dim": 8}).build()
    branches = [
        set(map(id, module.encoder.parameters())) for module in (model.actor, model.q1, model.q2)
    ]
    assert not branches[0] & branches[1]
    assert not branches[0] & branches[2]
    assert not branches[1] & branches[2]
    with pytest.raises(ValueError, match="output_dim"):
        SensorActorCriticModelFactory("ppo", encoder, {"feature_dim": 16}).build()
