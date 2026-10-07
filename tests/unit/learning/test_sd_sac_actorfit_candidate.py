"""The prepared candidate must not smuggle reward, model or budget changes."""

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from experiments.tmrl_test_comparison.prepare_sd_sac_actorfit import validate_scope
from trackmaniarl.core.spec import RunSpec

CONFIG = (
    Path(__file__).resolve().parents[3]
    / "experiments/tmrl_test_comparison/configs/diagnostic/sd-sac-actorfit-s17.yaml"
)


def configurations() -> tuple[dict, dict]:
    candidate = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    baseline = deepcopy(candidate)
    baseline["run_id"] = "stopped-alpha-floor"
    baseline["components"]["learner"]["kwargs"].pop("actor_objective")
    baseline["evaluation"].update(
        trials_per_map=30, target_median_s=37, target_mean_s=37, min_finish_rate=1
    )
    return baseline, candidate


def test_candidate_is_a_schema_valid_fresh_objective_only_experiment() -> None:
    baseline, candidate = configurations()
    validate_scope(baseline, candidate)
    spec = RunSpec.from_yaml(CONFIG)
    assert spec.training.total_transitions == 145408
    assert spec.training.updates_per_transition == 0.25
    options = candidate["components"]["learner"]["kwargs"]
    assert options["actor_learning_rate"] == 0.0001
    assert options["entropy_coefficient_min"] == 0.01
    assert options["entropy_penalty_coefficient"] == 0.0005
    assert options["actor_objective"] == "soft_q_forward_kl"


@pytest.mark.parametrize("change", ["reward", "model", "temperature", "utd", "trials", "resume"])
def test_candidate_rejects_unreviewed_changes(change: str) -> None:
    baseline, candidate = configurations()
    if change == "reward":
        candidate["components"]["environment"]["kwargs"]["config"]["terminal_failure_penalty"] = 3
    elif change == "model":
        candidate["components"]["model_factory"]["kwargs"]["config"]["feature_dim"] = 64
    elif change == "temperature":
        candidate["components"]["learner"]["kwargs"]["entropy_coefficient_min"] = 0.05
    elif change == "utd":
        candidate["training"]["updates_per_transition"] = 1
    elif change == "trials":
        candidate["evaluation"]["trials_per_map"] = 5
    else:
        candidate["run_id"] = baseline["run_id"]
    with pytest.raises(ValueError, match=r"Only the actor objective|new run identity"):
        validate_scope(baseline, candidate)


def test_candidate_cannot_enable_automatic_full_training_via_metadata() -> None:
    baseline, candidate = configurations()
    candidate["metadata"]["automatic_full_training"] = True
    with pytest.raises(ValueError, match="Automatic full training"):
        validate_scope(baseline, candidate)
