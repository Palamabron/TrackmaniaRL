"""A projection control must not smuggle reward, architecture or entropy changes."""

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from experiments.tmrl_test_comparison.prepare_sd_sac_projection import validate_scope


def candidate_pair() -> tuple[dict, dict]:
    path = Path(__file__).resolve().parents[3] / (
        "experiments/tmrl_test_comparison/configs/diagnostic/sd-sac-actorfit-s17.yaml"
    )
    baseline = yaml.safe_load(path.read_text(encoding="utf-8"))
    candidate = deepcopy(baseline)
    candidate["run_id"] = "tmrl-sd-sac-projected-s17"
    candidate["metadata"]["qualification"] = (
        "PREPARED_NOT_LAUNCHED; driving unverified; full BLOCKED"
    )
    return baseline, candidate


def test_projection_candidate_preserves_the_learning_and_driving_scope() -> None:
    baseline, candidate = candidate_pair()
    validate_scope(baseline, candidate)


@pytest.mark.parametrize("change", ["entropy", "reward", "model", "replay", "budget"])
def test_projection_candidate_rejects_unrelated_changes(change: str) -> None:
    baseline, candidate = candidate_pair()
    if change == "entropy":
        candidate["components"]["learner"]["kwargs"]["entropy_coefficient_min"] = 0.001
    elif change == "reward":
        candidate["components"]["environment"]["kwargs"]["config"]["terminal_failure_penalty"] = 1
    elif change == "model":
        candidate["components"]["model_factory"]["kwargs"]["config"]["feature_dim"] = 384
    elif change == "replay":
        candidate["components"]["sampler"]["kwargs"]["seed"] = 29
    else:
        candidate["training"]["total_transitions"] = 1000000
    with pytest.raises(ValueError, match="preserve"):
        validate_scope(baseline, candidate)
