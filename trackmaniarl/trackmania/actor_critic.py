"""First-party telemetry models for SAC, REDQ and stabilized discrete SAC."""

from __future__ import annotations

from torch import nn

from trackmaniarl.core.contracts import ModelContract
from trackmaniarl.models.actors import CategoricalActor, GaussianActor, GaussianActorConfig
from trackmaniarl.models.critics import ContinuousQCritic
from trackmaniarl.trackmania.telemetry import DEFAULT_TELEMETRY_FIELD_COUNT


def _encoder(input_dim: int, hidden_dim: int) -> nn.Module:
    if input_dim < 1 or hidden_dim < 1:
        raise ValueError("telemetry model dimensions must be positive")
    return nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.LayerNorm(hidden_dim), nn.SiLU())


def _actor(input_dim: int, hidden_dim: int) -> GaussianActor:
    return GaussianActor(
        _encoder(input_dim, hidden_dim),
        GaussianActorConfig(
            hidden_dim, 3, action_low=(0.0, 0.0, -1.0), action_high=(1.0, 1.0, 1.0)
        ),
    )


class TelemetrySacModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.actor = _actor(input_dim, hidden_dim)
        self.q1 = ContinuousQCritic(_encoder(input_dim, hidden_dim), hidden_dim, 3)
        self.q2 = ContinuousQCritic(_encoder(input_dim, hidden_dim), hidden_dim, 3)


class TelemetrySacModelFactory:
    model_contract = ModelContract.CONTINUOUS_ACTOR_CRITIC

    def __init__(
        self, input_dim: int = DEFAULT_TELEMETRY_FIELD_COUNT, hidden_dim: int = 256
    ) -> None:
        self.input_dim, self.hidden_dim = input_dim, hidden_dim

    def build(self) -> TelemetrySacModel:
        return TelemetrySacModel(self.input_dim, self.hidden_dim)


class TelemetryRedqModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, critic_count: int) -> None:
        super().__init__()
        if critic_count < 2:
            raise ValueError("REDQ requires at least two critics")
        self.actor = _actor(input_dim, hidden_dim)
        self.critics = nn.ModuleList(
            ContinuousQCritic(_encoder(input_dim, hidden_dim), hidden_dim, 3)
            for _ in range(critic_count)
        )


class TelemetryRedqModelFactory:
    model_contract = ModelContract.ENSEMBLE_ACTOR_CRITIC

    def __init__(
        self,
        input_dim: int = DEFAULT_TELEMETRY_FIELD_COUNT,
        hidden_dim: int = 256,
        critic_count: int = 10,
    ) -> None:
        self.input_dim, self.hidden_dim, self.critic_count = input_dim, hidden_dim, critic_count

    def build(self) -> TelemetryRedqModel:
        return TelemetryRedqModel(self.input_dim, self.hidden_dim, self.critic_count)


class TelemetryDiscreteSacModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, action_count: int) -> None:
        super().__init__()
        if action_count < 2:
            raise ValueError("discrete SAC requires at least two actions")
        self.actor = CategoricalActor(_encoder(input_dim, hidden_dim), hidden_dim, action_count)
        self.q1 = nn.Sequential(
            _encoder(input_dim, hidden_dim), nn.Linear(hidden_dim, action_count)
        )
        self.q2 = nn.Sequential(
            _encoder(input_dim, hidden_dim), nn.Linear(hidden_dim, action_count)
        )


class TelemetryDiscreteSacModelFactory:
    model_contract = ModelContract.DISCRETE_ACTOR_CRITIC

    def __init__(
        self,
        input_dim: int = DEFAULT_TELEMETRY_FIELD_COUNT,
        hidden_dim: int = 256,
        action_count: int = 78,
    ) -> None:
        self.input_dim, self.hidden_dim, self.action_count = input_dim, hidden_dim, action_count

    def build(self) -> TelemetryDiscreteSacModel:
        return TelemetryDiscreteSacModel(self.input_dim, self.hidden_dim, self.action_count)
