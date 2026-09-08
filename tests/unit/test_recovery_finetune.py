from __future__ import annotations

import argparse
from typing import Any, cast
from unittest.mock import Mock

import numpy as np
import pytest
import torch

from trackmaniarl.commands import recovery_finetune_training as training
from trackmaniarl.commands.recovery_finetune import _settings
from trackmaniarl.commands.recovery_finetune_types import _FineTuneSettings, _RecoverySample


def _sample(
    identifier: int = 0,
    **values: float | int,
) -> _RecoverySample:
    return _RecoverySample(
        {"feature": torch.tensor([float(identifier)])},
        int(values.get("action", 0)),
        float(values.get("gate", 1.0)),
        int(values.get("source_action", 0)),
        float(values.get("elapsed_s", 0.0)),
    )


def _settings_namespace(**overrides: int | float) -> argparse.Namespace:
    values: dict[str, int | float] = {
        "updates": 300,
        "batch_size": 128,
        "validation_fraction": 0.25,
        "minimum_gate": 0.01,
        "log_interval": 25,
        "minimum_usable_episodes": 24,
        "minimum_validation_episodes": 6,
        "minimum_gated_samples": 500,
        "minimum_samples_per_episode": 15,
        "maximum_normalized_recovery_time": 80.0,
        "minimum_source_disagreement": 0.05,
        "maximum_source_disagreement": 0.20,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def _default_settings(**overrides: int | float) -> _FineTuneSettings:
    return _settings(_settings_namespace(**overrides))


def test_recovery_batch_samples_episodes_uniformly_not_frames(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    short = (_sample(action=1),)
    long = tuple(_sample(index, action=2) for index in range(100))
    monkeypatch.setattr(
        training.torch,
        "randint",
        lambda _high, _size, *, generator: torch.tensor([0, 1, 1, 0]),
    )
    monkeypatch.setattr(training, "_sample_episode", lambda samples, _generator: samples[0])

    samples = training._sample_batch((short, long), 4, torch.Generator())

    assert [sample.action for sample in samples] == [1, 2, 2, 1]


def test_recovery_within_episode_weight_combines_gate_and_takeover_age(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    multinomial = Mock(return_value=torch.tensor([1]))
    monkeypatch.setattr(training.torch, "multinomial", multinomial)
    samples = (
        _sample(0, gate=0.5, elapsed_s=0.0),
        _sample(1, gate=1.0, elapsed_s=2.0),
    )

    selected = training._sample_episode(samples, torch.Generator())

    assert selected is samples[1]
    weights = multinomial.call_args.args[0]
    expected = torch.tensor([0.5, np.exp(-1.0)], dtype=weights.dtype)
    torch.testing.assert_close(weights, expected)


class _MetricLearner:
    def supervised_recovery_metrics(
        self, _observations: Any, actions: torch.Tensor
    ) -> dict[str, float]:
        value = float(actions.float().mean())
        return {"recovery/loss": value, "recovery/action_accuracy": value}

    def supervised_recovery_predictions(self, observations: Any) -> torch.Tensor:
        return torch.zeros(len(observations["feature"]), dtype=torch.int64)


def test_recovery_validation_averages_episodes_equally() -> None:
    failure = (_sample(action=0),)
    successes = tuple(_sample(index, action=1) for index in range(100))

    metrics = training._evaluate_episodes(
        cast(Any, _MetricLearner()), (failure, successes), batch_size=16
    )

    assert metrics is not None
    assert metrics["recovery/action_accuracy"] == pytest.approx(0.5)
    assert metrics["recovery/loss"] == pytest.approx(0.5)


@pytest.mark.parametrize("disagreement", [0.05, 0.20])
def test_recovery_candidate_accepts_accuracy_gain_at_disagreement_boundaries(
    disagreement: float,
) -> None:
    metrics = {
        "recovery/action_accuracy": 0.81,
        "recovery/source_disagreement": disagreement,
        "recovery/loss": 0.7,
    }

    score = training._candidate_score(metrics, 0.80, _default_settings())

    assert score == pytest.approx((0.81, -0.7))


@pytest.mark.parametrize(
    ("accuracy", "disagreement"),
    [(0.80, 0.10), (0.79, 0.10), (0.81, 0.049), (0.81, 0.201)],
)
def test_recovery_candidate_rejects_no_gain_or_unsafe_policy_drift(
    accuracy: float, disagreement: float
) -> None:
    metrics = {
        "recovery/action_accuracy": accuracy,
        "recovery/source_disagreement": disagreement,
        "recovery/loss": 0.7,
    }

    assert training._candidate_score(metrics, 0.80, _default_settings()) is None


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("updates", 0, "positive"),
        ("batch_size", 0, "positive"),
        ("validation_fraction", 1.0, "validation"),
        ("minimum_gate", -0.1, "minimum gate"),
        ("minimum_usable_episodes", 0, "minimums"),
        ("minimum_validation_episodes", 24, "validation minimum"),
        ("minimum_gated_samples", 0, "minimums"),
        ("minimum_samples_per_episode", 0, "minimums"),
        ("maximum_normalized_recovery_time", 0.0, "normalized recovery"),
        ("minimum_source_disagreement", 0.3, "disagreement"),
    ],
)
def test_recovery_settings_reject_invalid_values(
    name: str, value: int | float, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        _settings(_settings_namespace(**{name: value}))
