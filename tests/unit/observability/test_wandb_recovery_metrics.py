from trackmaniarl.observability.wandb_metrics import _event_metrics

_PAYLOAD = {
    "recovery/update": 25,
    "recovery/loss": 1.2,
    "recovery/action_accuracy": 0.4,
    "recovery/source_disagreement": 0.1,
    "recovery/validation_loss": 1.4,
    "recovery/validation_action_accuracy": 0.35,
    "ignored": 9,
}
_EXPECTED = {
    f"recovery/{key}": value
    for key, value in {
        "update": 25,
        "loss": 1.2,
        "action_accuracy": 0.4,
        "source_disagreement": 0.1,
        "validation_loss": 1.4,
        "validation_action_accuracy": 0.35,
    }.items()
}


def test_recovery_update_projects_training_and_validation_metrics() -> None:
    assert _event_metrics("recovery/update", _PAYLOAD) == _EXPECTED
