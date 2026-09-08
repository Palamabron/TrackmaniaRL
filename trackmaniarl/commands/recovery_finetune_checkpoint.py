"""Safe checkpoint persistence and provenance for recovery fine-tuning."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from time import time_ns
from typing import Any, cast

from trackmaniarl.commands.recovery_finetune_types import (
    _CheckpointRequest,
    _FineTuneSettings,
)
from trackmaniarl.core.checkpoints import validate_policy_checkpoint_v2

_POLICY_LEARNER_FIELDS = ("schema_version", "architecture_fingerprint", "online")


def _save_checkpoint(run: Any, request: _CheckpointRequest) -> Path:
    target = _checkpoint_target(run, request)
    _require_target_available(target, request.source)
    provenance = _provenance(request)
    checkpoint = {
        "schema_version": "2.0",
        "learner": _policy_only_learner_state(run.learner),
        "recovery_finetune": provenance,
    }
    run.checkpoint_codec.save(checkpoint, target)
    _write_report(run.run_dir / "recovery-finetune.json", provenance)
    return target


def _checkpoint_target(run: Any, request: _CheckpointRequest) -> Path:
    if request.output is not None:
        return request.output.resolve()
    name = f"recovery-policy-{request.result.best_update:08d}.pt"
    return cast(Path, run.run_dir / "checkpoints" / name)


def _require_target_available(target: Path, source: Path) -> None:
    resolved = target.resolve()
    if resolved == source.resolve():
        raise ValueError("recovery output checkpoint must differ from the source checkpoint")
    if resolved.exists():
        raise FileExistsError(f"recovery output checkpoint already exists: {resolved}")


def _provenance(request: _CheckpointRequest) -> dict[str, Any]:
    data, settings, result = request.data, request.settings, request.result
    return {
        "schema_version": "trackmaniarl-human-recovery-finetune-v1",
        "checkpoint_kind": "policy_only",
        "resume_supported": False,
        "source_checkpoint": str(request.source),
        "source_checkpoint_sha256": _file_sha256(request.source),
        "recovery_archives": _archive_provenance(data.paths),
        "updates_requested": settings.updates,
        "best_update": result.best_update,
        "train_samples": len(data.train),
        "validation_samples": len(data.validation),
        "train_episodes": data.train_episodes,
        "validation_episodes": data.validation_episodes,
        "settings": _provenance_settings(settings),
        "train_metrics": dict(result.train_metrics),
        "validation_metrics": _optional_metrics(result.validation_metrics),
    }


def _policy_only_learner_state(learner: Any) -> dict[str, Any]:
    """Return an evaluation/warm-start state without stale optimizer metadata."""

    source = learner.state_dict()
    missing = set(_POLICY_LEARNER_FIELDS) - source.keys()
    if missing:
        raise ValueError(f"recovery learner state is missing policy fields: {sorted(missing)}")
    policy = {name: source[name] for name in _POLICY_LEARNER_FIELDS}
    validate_policy_checkpoint_v2(policy)
    return policy


def _provenance_settings(settings: _FineTuneSettings) -> dict[str, float | int]:
    return {
        "updates": settings.updates,
        "batch_size": settings.batch_size,
        "validation_fraction": settings.validation_fraction,
        "minimum_gate": settings.minimum_gate,
        "log_interval": settings.log_interval,
        "minimum_usable_episodes": settings.minimum_usable_episodes,
        "minimum_validation_episodes": settings.minimum_validation_episodes,
        "minimum_gated_samples": settings.minimum_gated_samples,
        "minimum_samples_per_episode": settings.minimum_samples_per_episode,
        "maximum_normalized_recovery_time_s": settings.maximum_normalized_recovery_time_s,
        "minimum_source_disagreement": settings.minimum_source_disagreement,
        "maximum_source_disagreement": settings.maximum_source_disagreement,
    }


def _archive_provenance(paths: tuple[Path, ...]) -> list[dict[str, str]]:
    return [{"path": str(path), "sha256": _file_sha256(path)} for path in paths]


def _optional_metrics(metrics: Mapping[str, float] | None) -> dict[str, float] | None:
    return None if metrics is None else dict(metrics)


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_report(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(f".{time_ns()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


__all__ = ["_file_sha256", "_policy_only_learner_state", "_save_checkpoint"]
