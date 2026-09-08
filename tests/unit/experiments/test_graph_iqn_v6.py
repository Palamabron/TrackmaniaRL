from __future__ import annotations

import pytest
import torch

from trackmaniarl.experiments.graph_iqn_v3 import CONTEXT_V3_DIM
from trackmaniarl.experiments.graph_iqn_v5 import RECOVERY_V5_DIM
from trackmaniarl.experiments.graph_iqn_v6 import (
    IncidentGatedTrackGnnSimbaEncoderV6,
    IncidentRecoveryOnlyDiscreteValueLearner,
)
from trackmaniarl.models.composite import CompositeValueModel
from trackmaniarl.models.factory import CompositeValueModelFactory


def _observation(batch_size: int = 3) -> dict[str, torch.Tensor]:
    return {
        "physics": torch.randn(batch_size, 60),
        "track": torch.randn(batch_size, 3, 88),
        "context": torch.randn(batch_size, CONTEXT_V3_DIM),
        "recovery": torch.zeros(batch_size, RECOVERY_V5_DIM),
    }


def _model() -> CompositeValueModel:
    return CompositeValueModelFactory(
        encoder={
            "class_path": (
                "trackmaniarl.experiments.graph_iqn_v6:IncidentGatedTrackGnnSimbaEncoderV6"
            )
        },
        temporal={
            "class_path": "trackmaniarl.models.temporal:IdentityTemporalCore",
            "kwargs": {"input_dim": 192},
        },
        head={"class_path": "trackmaniarl.experiments.graph_iqn:DuelingImplicitQuantileHead"},
        strategy={
            "class_path": "trackmaniarl.models.strategies:RandomQuantileStrategy",
            "kwargs": {"train_quantile_count": 8, "target_quantile_count": 8},
        },
    ).build()


def _recovery_learner(model: CompositeValueModel) -> IncidentRecoveryOnlyDiscreteValueLearner:
    learner = IncidentRecoveryOnlyDiscreteValueLearner(model=model, burn_in=0)
    learner.setup({"seed": 0, "run_dir": None, "model_factory": None})
    return learner


def _incident_observation(batch_size: int = 3) -> dict[str, torch.Tensor]:
    observation = _observation(batch_size)
    observation["recovery"][:, 6] = 0.50
    observation["recovery"][:, 7] = 0.30
    return observation


def _changed_parameters(model: CompositeValueModel, before: dict[str, torch.Tensor]) -> set[str]:
    return {
        name for name, value in model.state_dict().items() if not torch.equal(value, before[name])
    }


def test_incident_gate_requires_memory_and_retained_speed_deficit() -> None:
    encoder = IncidentGatedTrackGnnSimbaEncoderV6()
    recovery = torch.zeros(4, RECOVERY_V5_DIM)
    recovery[1, 7] = 0.30
    recovery[2, 6] = 0.50
    recovery[3, 6] = 0.50
    recovery[3, 7] = 0.30

    gate = encoder.incident_gate(recovery)

    torch.testing.assert_close(gate[:3], torch.zeros(3, 1))
    torch.testing.assert_close(gate[3], torch.ones(1))


def test_learned_recovery_branch_cannot_change_nominal_policy() -> None:
    torch.manual_seed(8)
    encoder = IncidentGatedTrackGnnSimbaEncoderV6().eval()
    observation = _observation()
    with torch.no_grad():
        for parameter in encoder.recovery_adapter.parameters():
            parameter.fill_(0.2)

    baseline = encoder(observation)
    incident = {name: value.clone() for name, value in observation.items()}
    incident["recovery"][:, 6] = 0.50
    incident["recovery"][:, 7] = 0.30

    torch.testing.assert_close(encoder(observation), baseline, rtol=0.0, atol=0.0)
    assert torch.count_nonzero(encoder(incident) - baseline) > 0


def test_incident_frames_train_the_zero_initialized_adapter() -> None:
    encoder = IncidentGatedTrackGnnSimbaEncoderV6()
    observation = _observation()
    observation["recovery"][:, 6] = 0.50
    observation["recovery"][:, 7] = 0.30

    encoder(observation).sum().backward()

    final = encoder.recovery_adapter[-1]
    assert isinstance(final, torch.nn.Linear)
    assert final.weight.grad is not None
    assert torch.count_nonzero(final.weight.grad) > 0


def test_incident_recovery_learner_freezes_source_policy() -> None:
    model = _model()
    _recovery_learner(model)

    trainable = {name for name, parameter in model.named_parameters() if parameter.requires_grad}
    assert trainable
    assert all(name.startswith("encoder.recovery_adapter.") for name in trainable)


def test_supervised_recovery_update_changes_only_recovery_adapter() -> None:
    torch.manual_seed(4)
    model = _model()
    learner = _recovery_learner(model)
    before = {name: value.detach().clone() for name, value in model.state_dict().items()}
    metrics = learner.supervised_recovery_update(
        _incident_observation(batch_size=8),
        torch.full((8,), 39, dtype=torch.int64),
    )
    changed = _changed_parameters(model, before)
    assert changed
    assert all(name.startswith("encoder.recovery_adapter.") for name in changed)
    assert metrics["recovery/loss"] > 0.0
    assert 0.0 <= metrics["recovery/action_accuracy"] <= 1.0


def test_supervised_recovery_update_rejects_bad_action_batch() -> None:
    learner = IncidentRecoveryOnlyDiscreteValueLearner(model=_model(), burn_in=0)
    learner.setup({"seed": 0, "run_dir": None, "model_factory": None})

    with pytest.raises(ValueError, match="shape"):
        learner.supervised_recovery_update(_observation(), torch.zeros((3, 1)))


@pytest.mark.parametrize(
    ("thresholds", "message"),
    [
        ((0.2, 0.1, 0.08, 0.4), "memory"),
        ((0.12, 0.25, -0.1, 0.4), "retained"),
        ((0.12, float("inf"), 0.08, 0.4), "finite"),
    ],
)
def test_incident_gate_rejects_invalid_thresholds(
    thresholds: tuple[float, float, float, float], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        IncidentGatedTrackGnnSimbaEncoderV6(incident_gate_thresholds=thresholds)
