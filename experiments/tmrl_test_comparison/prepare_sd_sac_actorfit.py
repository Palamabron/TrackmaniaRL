"""Validate and record a fresh actor-fit candidate; never launches a process or game."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.spec import RunSpec


def _resolved_config(path: Path) -> dict[str, Any]:
    config: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    groups = [
        config["components"]["environment"]["kwargs"]["config"],
        config["components"]["feature_pipeline"]["kwargs"],
        *config["evaluation"]["maps"],
    ]
    for group in groups:
        for name in ("map_path", "geometry_path"):
            if name in group:
                group[name] = str((path.parent / group[name]).resolve())
    return config


def validate_scope(baseline: dict[str, Any], candidate: dict[str, Any]) -> None:
    """Only objective, output identity, documentation and explicit eval gate may differ."""
    expected = copy.deepcopy(baseline)
    if not candidate["run_id"] or candidate["run_id"] == baseline["run_id"]:
        raise ValueError("A new run identity is required; checkpoint resume is forbidden")
    expected["run_id"] = candidate["run_id"]
    expected["artifacts_dir"] = candidate["artifacts_dir"]
    expected["metadata"] = candidate["metadata"]
    expected["components"]["learner"]["kwargs"]["actor_objective"] = "soft_q_forward_kl"
    expected["evaluation"].update(
        trials_per_map=10, target_median_s=None, target_mean_s=None, min_finish_rate=0.8
    )
    if candidate != expected:
        raise ValueError(
            "Only the actor objective and documented output/evaluation scope may change"
        )
    if candidate["training"]["total_transitions"] != 145408:
        raise ValueError("The fresh pilot must retain its 145408-transition budget")
    if candidate["metadata"].get("automatic_full_training") is not False:
        raise ValueError("Automatic full training is forbidden")


def prepare(baseline: Path, candidate: Path, receipt: Path) -> None:
    baseline, candidate = baseline.resolve(), candidate.resolve()
    before, after = _resolved_config(baseline), _resolved_config(candidate)
    validate_scope(before, after)
    spec = RunSpec.from_yaml(candidate)
    run = (candidate.parent / spec.artifacts_dir / spec.run_id).resolve()
    if run.exists():
        raise ValueError("Candidate run directory already exists; never restart a used run")
    assets = {
        path
        for entry in after["evaluation"]["maps"]
        for key, path in entry.items()
        if key in ("map_path", "geometry_path")
    }
    pins = {}
    for path in (str(baseline), str(candidate), *sorted(assets)):
        with Path(path).open("rb") as stream:
            pins[path] = hashlib.file_digest(stream, "sha256").hexdigest()
    result = {
        "status": "PREPARED_NOT_LAUNCHED",
        "candidate": str(candidate),
        "run_id": spec.run_id,
        "run_fingerprint": run_fingerprint(spec, candidate.parent),
        "immutable_inputs": pins,
        "fresh_start_required": True,
        "checkpoint_resume_allowed": False,
        "controller_created": False,
        "maximum_seconds": 14400,
        "train_maximum_seconds": 11400,
        "evaluation_trials": 10,
        "evaluation_maximum_seconds": 2100,
        "automatic_full_training": False,
        "human_STOP_remains_effective": True,
        "launch_requires": "New human start instruction and new pinned bounded queue/runtime; "
        "this preparation neither grants STOP exceptions nor launches training.",
    }
    # Exclusive creation preserves an earlier preparation receipt.
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print("PREPARED_NOT_LAUNCHED: scope, assets and schema valid; human STOP remains effective")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.baseline, args.candidate, args.receipt)
