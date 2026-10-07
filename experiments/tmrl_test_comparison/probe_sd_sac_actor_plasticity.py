"""Offline fixed-Q actor plasticity; CPU/idle/one thread, disposable Adam copies.

Run by absolute filename, with cwd/PYTHONPATH restricted to the frozen runtime.
No learner/controller, model persistence, checkpoint resume or game access.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Any

if __name__ == "__main__":
    for variable in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        os.environ[variable] = "1"
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["WANDB_MODE"] = "disabled"

import numpy as np
import psutil  # type: ignore[import-untyped]
import torch

from trackmaniarl.algorithms.sd_sac_objectives import (
    soft_q_log_probabilities,
)
from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.pytree import tree_map
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.models.backbones import project_hyperspherical_weights


def load_helper() -> Any:
    spec = importlib.util.spec_from_file_location(
        "joint_probe_support", Path(__file__).with_name("probe_sd_sac_joint_calibration.py")
    )
    assert spec is not None
    assert spec.loader is not None
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def policy_loss(  # noqa: PLR0913
    logs: torch.Tensor, q: torch.Tensor, alpha: float, objective: str
) -> torch.Tensor:
    if objective == "greedy":
        return -logs.gather(1, q.argmax(1, keepdim=True)).mean()
    if objective == "forward":
        return -(soft_q_log_probabilities(q, torch.tensor(alpha)).exp() * logs).sum(1).mean()
    if objective == "sac":
        # Subtracting a state-only baseline preserves the SAC gradient.
        advantages = q - q.max(1, keepdim=True).values
        return (logs.exp() * (alpha * logs - advantages)).sum(1).mean()
    raise ValueError(objective)


def indexed(tree: Any, indices: Any) -> Any:
    return tree_map(lambda leaf: leaf[indices], tree)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("config", "checkpoint", "original-checkpoint", "prior-probe", "starts", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--projected-only", action="store_true")
    args = parser.parse_args()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    assert not torch.cuda.is_available()
    helper = load_helper()
    begun = time.monotonic()
    inputs = (args.checkpoint, args.original_checkpoint, args.config, args.prior_probe, args.starts)
    pins = {str(path): helper.sha(path) for path in inputs}
    assert (
        pins[str(args.checkpoint)] == pins[str(args.original_checkpoint)] == helper.CHECKPOINT_SHA
    )
    state = helper.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    assert run_fingerprint(spec, Path.cwd()) == state["run_fingerprint"]
    factory = spec.components.model_factory
    assert factory is not None
    model = _instantiate(factory).build()
    model.load_state_dict(state["learner"]["model"], strict=True)
    model.eval().requires_grad_(False)
    digest = helper.model_digest(model)
    adam_pin = helper.tree_digest(state["learner"]["actor_optimizer"])
    replay = state["replay_store"]
    prior = json.loads(args.prior_probe.read_text(encoding="utf-8"))
    fit_rows = np.array(prior["split"]["selected_rows"][:4206])
    held_rows = np.array(prior["split"]["selected_rows"][4206:])
    start_rows = np.array(json.loads(args.starts.read_text(encoding="utf-8"))["transition_ids"])
    assert len(fit_rows) == 4206
    assert len(held_rows) == 1051
    assert len(start_rows) == 138
    assert not set(replay["episode_codes"][fit_rows]) & set(replay["episode_codes"][held_rows])
    groups: dict[str, Any] = {}
    for name, rows in (("fit", fit_rows), ("held", held_rows), ("starts", start_rows)):
        obs = helper.decode_tree(replay["observations"], rows)
        chunks = []
        with torch.no_grad():
            for offset in range(0, len(rows), 128):
                item = indexed(obs, slice(offset, offset + 128))
                chunks.append(0.5 * model.q1(item) + 0.5 * model.q2(item))
        q = torch.cat(chunks)
        entropy = torch.tensor(
            [replay["info"][int(row)]["_trackmaniarl_behavior_entropy"] for row in rows]
        )
        groups[name] = (obs, q, entropy)
    options = state["learner"]["sd_sac_options"]
    beta = options["entropy_penalty_coefficient"]
    report: dict[str, Any] = {
        "status": "RUNNING",
        "checkpoint_sha256": helper.CHECKPOINT_SHA,
        "input_pins": pins,
        "fingerprint": state["run_fingerprint"],
        "script_sha256": helper.sha(Path(__file__)),
        "cpu_threads": 1,
        "priority": "IDLE",
        "automation": "PAUSED",
        "runtime_learner_updates": 0,
        "controller_created": False,
        "copy_optimizer_steps": 0,
        "steps_per_copy": 64,
        "cap_seconds": 600,
        "design": "Fixed saved Q; copied saved actor and Adam; actor-only fit on4206 rows, "
        "1051 held rows. Starts descriptive, not a held-out set.",
        "results": [],
    }

    def save() -> None:
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")

    def metrics(actor: Any) -> dict[str, Any]:
        result = {}
        with torch.no_grad():
            for name, (obs, q, _) in groups.items():
                logs = torch.cat(
                    [
                        actor.log_probabilities(indexed(obs, slice(i, i + 128)))
                        for i in range(0, len(q), 128)
                    ]
                )
                prob = logs.exp()
                best = q.argmax(1)
                greedy = logs.argmax(1)
                actions, counts = torch.unique(greedy, return_counts=True)
                result[name] = {
                    "agreement": float((greedy == best).float().mean()),
                    "greedy_q_regret": float(
                        (q.max(1).values - q.gather(1, greedy[:, None]).squeeze(1)).mean()
                    ),
                    "entropy": float(-(prob * logs).sum(1).mean()),
                    "critic_top1_probability": float(prob.gather(1, best[:, None]).mean()),
                    "greedy_distribution": dict(
                        zip(map(str, actions.tolist()), counts.tolist(), strict=True)
                    ),
                }
        return result

    report["baseline"] = metrics(model.actor)
    report["start_targets"] = {}
    for alpha in (0.01, 0.001):
        _, q, _ = groups["starts"]
        logs = soft_q_log_probabilities(q, torch.tensor(alpha))
        report["start_targets"][str(alpha)] = {
            "entropy": float(-(logs.exp() * logs).sum(1).mean()),
            "p71": float(logs.exp()[:, 71].mean()),
            "p21": float(logs.exp()[:, 21].mean()),
            "p71_over_p21": float((logs[:, 71] - logs[:, 21]).exp().mean()),
        }
    # Measure actual parameter gradients, not incomparable scalar loss magnitudes.
    actor = copy.deepcopy(model.actor).requires_grad_(True)
    obs, q, behavior = groups["starts"]
    logs = actor.log_probabilities(obs)
    entropy = -(logs.exp() * logs).sum(1)
    losses = {
        "sac_q": -(logs.exp() * (q - q.max(1, keepdim=True).values)).sum(1).mean(),
        "sac_entropy": 0.01 * (logs.exp() * logs).sum(1).mean(),
        "forward": policy_loss(logs, q, 0.01, "forward"),
        "behavior_anchor": beta * (entropy - behavior).square().mean(),
    }
    parameters = list(actor.parameters())
    gradients = {}
    for name, loss in losses.items():
        values = torch.autograd.grad(loss, parameters, retain_graph=True, allow_unused=True)
        gradients[name] = torch.cat(
            [
                torch.zeros_like(p).flatten() if g is None else g.flatten()
                for p, g in zip(parameters, values, strict=True)
            ]
        )
    report["start_gradient_norms"] = {name: float(g.norm()) for name, g in gradients.items()}
    left, right = gradients["sac_q"], gradients["sac_entropy"]
    report["sac_q_entropy_gradient_cosine"] = float(
        torch.dot(left, right) / (left.norm() * right.norm()).clamp_min(1e-30)
    )
    del actor, gradients, losses, parameters, logs
    save()
    variants = (
        (("forward", 0.01),)
        if args.projected_only
        else (("forward", 0.01), ("forward", 0.001), ("greedy", 0.0))
    )
    report["project_after_each_adam_step"] = args.projected_only
    for objective, alpha in variants:
        for seed in (17, 29):
            print(f"Actor copy: {objective}, alpha={alpha}, seed={seed},64 steps", flush=True)
            actor = copy.deepcopy(model.actor).requires_grad_(True)
            optimizer = torch.optim.Adam(actor.parameters(), lr=options["actor_learning_rate"])
            optimizer.load_state_dict(copy.deepcopy(state["learner"]["actor_optimizer"]))
            rng = np.random.default_rng(seed)
            obs, q, behavior = groups["fit"]
            for _ in range(64):
                if time.monotonic() - begun > 600:
                    raise TimeoutError("600s offline cap")
                indices = rng.integers(0, len(q), 128)
                logs = actor.log_probabilities(indexed(obs, indices))
                entropy = -(logs.exp() * logs).sum(1)
                loss = policy_loss(logs, q[indices], alpha, objective)
                loss = loss + beta * (entropy - behavior[indices]).square().mean()
                assert bool(torch.isfinite(loss))
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
                if args.projected_only:
                    project_hyperspherical_weights(actor)
                report["copy_optimizer_steps"] += 1
            report["results"].append(
                {"objective": objective, "alpha": alpha, "seed": seed, "metrics": metrics(actor)}
            )
            save()
            del optimizer, actor
    assert report["copy_optimizer_steps"] == 128 * len(variants)
    assert digest == helper.model_digest(model)
    assert adam_pin == helper.tree_digest(state["learner"]["actor_optimizer"])
    assert pins == {path: helper.sha(Path(path)) for path in pins}
    assert report["script_sha256"] == helper.sha(Path(__file__))
    report["immutable_inputs_models_saved_adam_unchanged"] = True
    report["status"] = "COMPLETE"
    report["elapsed_seconds"] = time.monotonic() - begun
    save()
    print("COMPLETE: no saved policy change", flush=True)


if __name__ == "__main__":
    main()
