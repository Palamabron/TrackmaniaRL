"""Prepare a fresh bounded projection-control candidate; never launch a run."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from experiments.tmrl_test_comparison.prepare_sd_sac_actorfit import _resolved_config
from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.spec import RunSpec


def validate_scope(baseline: dict[str, Any], candidate: dict[str, Any]) -> None:
    expected = copy.deepcopy(baseline)
    if not candidate["run_id"] or candidate["run_id"] == baseline["run_id"]:
        raise ValueError("Fresh run identity required; old checkpoint resume forbidden")
    expected["run_id"] = candidate["run_id"]
    expected["metadata"] = candidate["metadata"]
    if candidate != expected:
        raise ValueError("Projection control must preserve all learning/reward/model/data settings")
    metadata = candidate["metadata"]
    if metadata.get("qualification") != "PREPARED_NOT_LAUNCHED; driving unverified; full BLOCKED":
        raise ValueError("Candidate must explicitly retain the unqualified driving status")
    if metadata.get("automatic_full_training") is not False:
        raise ValueError("No automatic full training")


def prepare(baseline: Path, candidate: Path, receipt: Path) -> None:
    source = yaml.safe_load(baseline.read_text(encoding="utf-8"))
    proposed = copy.deepcopy(source)
    proposed["run_id"] = "tmrl-sd-sac-projected-s17"
    proposed["metadata"].update(
        stage="prepared-projection-control",
        hypothesis="Only source repair: project hyperspherical weights after critic/actor Adam. "
        "All learning settings and shared reward/model/GNN/replay/UTD match actorfit. "
        "Fixed-Q copy improvement does not prove correct Q or driving.",
        qualification="PREPARED_NOT_LAUNCHED; driving unverified; full BLOCKED",
        automatic_full_training=False,
        checkpoint_resume_allowed=False,
        fresh_start_required=True,
    )
    validate_scope(source, proposed)
    if candidate.exists():
        if yaml.safe_load(candidate.read_text(encoding="utf-8")) != proposed:
            raise ValueError("Existing candidate differs; preserve it and use another filename")
    else:
        with candidate.open("x", encoding="utf-8") as stream:
            yaml.safe_dump(proposed, stream, sort_keys=False, allow_unicode=True)
    validate_scope(_resolved_config(baseline), _resolved_config(candidate))
    spec = RunSpec.from_yaml(candidate)
    run = (candidate.parent / spec.artifacts_dir / spec.run_id).resolve()
    if run.exists():
        raise ValueError("Candidate run already exists; restart forbidden")
    root = Path(__file__).resolve().parents[2]
    learner = root / "trackmaniarl/algorithms/stable_discrete_soft_actor_critic.py"
    assert "project_hyperspherical_weights(self.model.actor)" in learner.read_text(encoding="utf-8")
    pins = {}
    for path in (baseline, candidate, learner, Path(__file__)):
        with path.open("rb") as stream:
            pins[str(path.resolve())] = hashlib.file_digest(stream, "sha256").hexdigest()
    result = {
        "status": "PREPARED_NOT_LAUNCHED",
        "candidate": str(candidate.resolve()),
        "run_fingerprint": run_fingerprint(spec, candidate.parent),
        "pins": pins,
        "new_run_directory_created": False,
        "controller_created": False,
        "automation": "PAUSED",
        "checkpoint_resume_allowed": False,
        "fresh_start_required": True,
        "gate": "145408 complete/finite/accounted/drained, >=8/10 finishes, correctUID, "
        "max timing<=100ms, no errors, skips reported, SHA/source/STOP/process closure verified",
        "maximum_seconds": 14400,
        "train_maximum_seconds": 11400,
        "evaluation_maximum_seconds": 2100,
        "launch_requires": "New bounded queue, frozen repaired runtime, independent guard, "
        "fresh source/asset/STOP pins and live preflight. No old queue or STOP exemption reused.",
    }
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.baseline, args.candidate, args.receipt)
