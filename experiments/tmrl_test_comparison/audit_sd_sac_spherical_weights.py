"""Read-only saved weight geometry and inference-preserving copy projection."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path

if __name__ == "__main__":
    for name in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        os.environ[name] = "1"
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["WANDB_MODE"] = "disabled"

import psutil  # type: ignore[import-untyped]
import torch

from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.models.backbones import HypersphericalLinear, project_hyperspherical_weights


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "starts", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    spec = importlib.util.spec_from_file_location(
        "audit_support", Path(__file__).with_name("probe_sd_sac_joint_calibration.py")
    )
    assert spec is not None
    assert spec.loader is not None
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    before = h.sha(args.checkpoint)
    assert before == h.CHECKPOINT_SHA
    state = h.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    run = RunSpec.from_yaml(args.config)
    assert run_fingerprint(run, Path.cwd()) == state["run_fingerprint"]
    factory = run.components.model_factory
    assert factory is not None
    model = _instantiate(factory).build()
    model.load_state_dict(state["learner"]["model"], strict=True)
    model.eval().requires_grad_(False)
    layers = {}
    for name, layer in model.named_modules():
        if isinstance(layer, HypersphericalLinear):
            norm = layer.weight.norm(dim=1)
            layers[name] = {
                "mean": float(norm.mean()),
                "min": float(norm.min()),
                "max": float(norm.max()),
            }
    rows = json.loads(args.starts.read_text(encoding="utf-8"))["transition_ids"]
    import numpy as np

    obs = h.decode_tree(state["replay_store"]["observations"], np.array(rows))
    candidate = copy.deepcopy(model)
    project_hyperspherical_weights(candidate)
    with torch.no_grad():
        errors = {
            "actor_logits": float(
                (model.actor.log_probabilities(obs) - candidate.actor.log_probabilities(obs))
                .abs()
                .max()
            ),
            "q1": float((model.q1(obs) - candidate.q1(obs)).abs().max()),
            "q2": float((model.q2(obs) - candidate.q2(obs)).abs().max()),
        }
    assert h.sha(args.checkpoint) == before
    result = {
        "checkpoint_sha256": before,
        "layers": layers,
        "copy_projection_inference_max_abs_difference": errors,
        "optimizer_steps": 0,
        "automation": "PAUSED",
        "cpu_threads": 1,
        "priority": "IDLE",
        "scope": "Weight radius audit; projection invariance does not establish "
        "learning or driving improvement.",
    }
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
