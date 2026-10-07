"""Small-weight and frozen-encoder controls for disposable critic calibration.

Uses exactly the prior 110/4096/27/1024 split; no game, learner or saved model.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

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

import numpy as np
import psutil  # type: ignore[import-untyped]
import torch

from trackmaniarl.algorithms.stable_discrete_soft_actor_critic import StableDiscreteSoftActorCritic
from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("config", "checkpoint", "original-checkpoint", "prior-probe", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    assert not torch.cuda.is_available()
    helper_spec = importlib.util.spec_from_file_location(
        "joint_support", Path(__file__).with_name("probe_sd_sac_joint_calibration.py")
    )
    assert helper_spec is not None
    assert helper_spec.loader is not None
    h = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(h)
    started = time.monotonic()
    files = (args.checkpoint, args.original_checkpoint, args.config, args.prior_probe)
    pins = {str(path): h.sha(path) for path in files}
    assert pins[str(args.checkpoint)] == pins[str(args.original_checkpoint)] == h.CHECKPOINT_SHA
    state = h.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    assert run_fingerprint(spec, Path.cwd()) == state["run_fingerprint"]
    factory = spec.components.model_factory
    assert factory is not None
    model, target = _instantiate(factory).build(), _instantiate(factory).build()
    for module, key in ((model, "model"), (target, "target_model")):
        module.load_state_dict(state["learner"][key], strict=True)
        module.eval().requires_grad_(False)
    digests = [h.model_digest(x) for x in (model, target)]
    adam_pin = h.tree_digest(state["learner"]["critic_optimizer"])
    prior = json.loads(args.prior_probe.read_text(encoding="utf-8"))
    rows = np.array(prior["split"]["selected_rows"])
    assert prior["split"]["group_sizes"] == [110, 4096, 27, 1024]
    batch = h.materialize(state["replay_store"], rows, spec.training.gamma)
    options = state["learner"]["sd_sac_options"]
    context: Any = SimpleNamespace(
        model=model, target_model=target, target_entropy=options["target_entropy"]
    )
    context._desired_entropy = lambda n: StableDiscreteSoftActorCritic._desired_entropy(context, n)
    targets = torch.cat(
        [
            StableDiscreteSoftActorCritic._critic_targets(
                context, h.subset(batch, slice(i, i + 128)), torch.tensor(0.01)
            )
            for i in range(0, len(rows), 128)
        ]
    )
    assert torch.equal(targets[batch.source.terminated], batch.rewards[batch.source.terminated])
    features = []
    with torch.no_grad():
        for critic in (model.q1, model.q2):
            features.append(
                torch.cat(
                    [
                        critic[0](h.subset(batch, slice(i, i + 128)).observations)
                        for i in range(0, len(rows), 128)
                    ]
                )
            )

    def prediction(candidate: Any, head_only: bool, indices: Any) -> torch.Tensor:  # noqa: FBT001
        if head_only:
            return torch.stack(
                [
                    critic[1](feature[indices]).gather(1, batch.actions[indices, None]).squeeze(1)
                    for critic, feature in zip((candidate.q1, candidate.q2), features, strict=True)
                ]
            )
        return torch.stack(h.selected(candidate, h.subset(batch, indices)))

    def metrics(candidate: Any, head_only: bool) -> tuple[dict[str, Any], np.ndarray]:  # noqa: FBT001
        with torch.no_grad():
            errors = (
                (
                    torch.cat(
                        [
                            prediction(candidate, head_only, slice(i, i + 128))
                            for i in range(0, len(rows), 128)
                        ],
                        1,
                    )
                    - targets
                )
                .abs()
                .numpy()
            )
        result = {
            name: float(errors[:, a:b].mean())
            for name, a, b in (
                ("fit_terminal_mae", 0, 110),
                ("fit_nonterminal_mae", 110, 4206),
                ("held_terminal_mae", 4206, 4233),
                ("held_nonterminal_mae", 4233, 5257),
            )
        }
        return result, errors[:, 4206:4233].mean(0)

    baseline, base_errors = metrics(model, False)
    report: dict[str, Any] = {
        "status": "RUNNING",
        "input_pins": pins,
        "baseline": baseline,
        "copy_optimizer_steps": 0,
        "runtime_learner_updates": 0,
        "controller_created": False,
        "automation": "PAUSED",
        "cpu_threads": 1,
        "priority": "IDLE",
        "results": [],
        "cap_seconds": 600,
        "design": "48 steps per copy,128 nonterminals+128 terminals with replacement,"
        "separate class means,frozen Bellman targets. Head-only control freezes encoders "
        "and reuses cached features; all copies restore saved full critic Adam.",
    }

    def save() -> None:
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")

    save()
    variants = ((0.003, False), (0.01, False), (0.03, False), (0.1, True))
    for weight, head_only in variants:
        for seed in (17, 29):
            print(f"Critic copy: lambda={weight},head_only={head_only},seed={seed}", flush=True)
            candidate = copy.deepcopy(model)
            for critic in (candidate.q1, candidate.q2):
                (critic[1] if head_only else critic).requires_grad_(True)
            optimizer = torch.optim.Adam(
                list(candidate.q1.parameters()) + list(candidate.q2.parameters()),
                lr=options["learning_rate"],
            )
            optimizer.load_state_dict(copy.deepcopy(state["learner"]["critic_optimizer"]))
            rng = np.random.default_rng(seed)
            for _ in range(48):
                if time.monotonic() - started > 600:
                    raise TimeoutError("600s cap")
                indices = np.r_[rng.integers(110, 4206, 128), rng.integers(0, 110, 128)]
                error = prediction(candidate, head_only, indices) - targets[indices]
                loss = h.joint_loss(error[:, :128], error[:, 128:], weight)
                assert bool(torch.isfinite(loss))
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
                report["copy_optimizer_steps"] += 1
            measured, errors = metrics(candidate, head_only)
            measured.update(
                {
                    "lambda": weight,
                    "head_only": head_only,
                    "seed": seed,
                    "held_terminal_errors": errors.tolist(),
                    "guard_passed": measured["held_nonterminal_mae"]
                    <= min(0.145, 1.2 * baseline["held_nonterminal_mae"]),
                }
            )
            if head_only:
                assert all(
                    h.model_digest(a[0]) == h.model_digest(b[0])
                    for a, b in zip((candidate.q1, candidate.q2), (model.q1, model.q2), strict=True)
                )
            report["results"].append(measured)
            save()
            del candidate, optimizer
    report["decisions"] = []
    for weight, head_only in variants:
        pair = [
            r for r in report["results"] if r["lambda"] == weight and r["head_only"] == head_only
        ]
        interval = h.paired_interval(
            np.array([base_errors - np.array(r["held_terminal_errors"]) for r in pair])
        )
        report["decisions"].append(
            {
                "lambda": weight,
                "head_only": head_only,
                "terminal_reduction": interval,
                "both_seeds_guard": all(r["guard_passed"] for r in pair),
            }
        )
    assert report["copy_optimizer_steps"] == 384
    assert digests == [h.model_digest(x) for x in (model, target)]
    assert adam_pin == h.tree_digest(state["learner"]["critic_optimizer"])
    assert pins == {path: h.sha(Path(path)) for path in pins}
    report["immutable_inputs_models_saved_adam_unchanged"] = True
    report["elapsed_seconds"] = time.monotonic() - started
    report["status"] = "COMPLETE"
    save()
    print("COMPLETE", flush=True)


if __name__ == "__main__":
    main()
