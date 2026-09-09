from __future__ import annotations

import json
from dataclasses import replace
from itertools import product
from pathlib import Path

import numpy as np
import pytest
import torch

from tests.integration.trackmania.workflow_fixtures import (
    ReplayEnvironment,
    base_config,
    demonstration,
    save_config,
)
from trackmaniarl.cli import entrypoint
from trackmaniarl.commands.recovery_finetune_checkpoint import _file_sha256
from trackmaniarl.core.builtins import TorchCheckpointCodec
from trackmaniarl.core.checkpoints import validate_policy_checkpoint_v2
from trackmaniarl.core.contracts import EvaluatorRuntimeRequest
from trackmaniarl.core.runtime import resolve_run
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.trackmania.actions import (
    build_brake_tap_action_table,
    continuous_control_to_discrete_indices_batch,
)
from trackmaniarl.trackmania.evaluation import TrackmaniaEvaluator
from trackmaniarl.trackmania.human_recovery_data import (
    RecoveryDemonstration,
    save_recovery_demonstration,
)


def _config(directory: Path) -> dict:
    config = base_config(directory)
    components = config["components"]
    components["learner"] = {
        "class_path": (
            "trackmaniarl.experiments.graph_iqn_v6:IncidentRecoveryOnlyDiscreteValueLearner"
        )
    }
    components["feature_pipeline"] = {
        "class_path": "trackmaniarl.experiments.graph_iqn_v5:BoundaryGraphFeaturePipelineV5",
        "kwargs": {
            "geometry_path": config["evaluation"]["maps"][0]["geometry_path"],
            "expected_map_uid": "trackmaniarl-test",
        },
    }
    model = components["model_factory"]["kwargs"]
    model["encoder"] = {
        "class_path": "trackmaniarl.experiments.graph_iqn_v6:IncidentGatedTrackGnnSimbaEncoderV6"
    }
    model["temporal"]["kwargs"]["input_dim"] = 192
    model["head"] = {"class_path": "trackmaniarl.experiments.graph_iqn:DuelingImplicitQuantileHead"}
    model["strategy"]["kwargs"] = {"train_quantile_count": 8, "target_quantile_count": 8}
    return config


def test_recovery_command_loads_archives_trains_saves_and_evaluates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    config_path = save_config(tmp_path, config)
    demo = demonstration(config)
    source = tmp_path / "source.pt"
    run = resolve_run(RunSpec.from_yaml(config_path))
    try:
        run.learner.setup({"seed": 0, "model_factory": run.model_factory})
        before = {key: value.clone() for key, value in run.learner.model.state_dict().items()}
        run.checkpoint_codec.save(
            {"schema_version": "2.0", "learner": run.learner.state_dict()}, source
        )
    finally:
        run.logger.close()
    archives = tmp_path / "recoveries"
    for episode, (progress, steps, direction) in enumerate(
        product((0.5, 0.7, 0.8), (10, 15, 20), (-1, 1))
    ):
        frames = demo.frames.copy()
        frames[90:120:2, 7] = 50.0
        frames[90:120:2, 16] = 50.0
        controls = demo.controls.copy()
        controls[100:120, 2] = direction
        frames[:-1, 30] = controls[:, 2]
        _, table = build_brake_tap_action_table()
        actions = continuous_control_to_discrete_indices_batch(controls, table)
        incident = replace(demo, frames=frames, controls=controls, actions=actions)
        recovery = RecoveryDemonstration(
            incident,
            100,
            steps,
            100 + steps,
            progress,
            progress,
            np.array([1, 0, direction], dtype=np.float32),
            steps * 10.0,
            steps * 10.0,
            _file_sha256(source),
        )
        save_recovery_demonstration(archives / f"episode-{episode}.npz", recovery)
    output = tmp_path / "adapted.pt"
    entrypoint(
        [
            "recovery-finetune",
            str(config_path),
            str(source),
            "--recovery",
            str(archives),
            "--updates",
            "2",
            "--batch-size",
            "4",
            "--log-interval",
            "1",
            "--minimum-usable-episodes",
            "3",
            "--minimum-validation-episodes",
            "1",
            "--minimum-gated-samples",
            "1",
            "--minimum-samples-per-episode",
            "1",
            "--minimum-source-disagreement",
            "0",
            "--maximum-source-disagreement",
            "1",
            "--output",
            str(output),
        ]
    )
    state = TorchCheckpointCodec().load(output)
    validate_policy_checkpoint_v2(state["learner"])
    restored = resolve_run(RunSpec.from_yaml(config_path))
    environment = ReplayEnvironment(demo)
    monkeypatch.setattr(restored.environment_factory, "create", lambda **kwargs: environment)
    try:
        restored.learner.setup({"seed": 0, "model_factory": restored.model_factory})
        restored.learner.load_policy_state_dict(state["learner"])
        for name, value in restored.learner.model.state_dict().items():
            if "recovery_adapter" not in name:
                torch.testing.assert_close(value, before[name], rtol=0, atol=0)
        evaluator = TrackmaniaEvaluator(
            EvaluatorRuntimeRequest(
                suite=restored.spec.evaluation,
                environment_factory=restored.environment_factory,
                feature_pipeline=restored.feature_pipeline,
                run_dir=tmp_path / "evaluation",
            )
        )
        assert evaluator.evaluate(restored.learner.policy())["eval/finish_rate"] == 1.0
        artifact = json.loads((tmp_path / "evaluation" / "evaluation.json").read_text())
        assert artifact
    finally:
        restored.logger.close()
    assert environment.closed
