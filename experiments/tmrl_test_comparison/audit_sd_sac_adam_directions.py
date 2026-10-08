"""Audit saved Adam directions and start-action margins without model updates."""

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
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["WANDB_MODE"] = "disabled"

import numpy as np
import psutil
import torch

from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.models.backbones import HypersphericalLinear


def adam_delta(  # noqa: PLR0913 - explicit Adam inputs and diagnostic control

    param: torch.Tensor,
    grad: torch.Tensor,
    saved: dict[str, Any],
    group: dict[str, Any],
    *,
    reset_momentum: bool = False,
) -> torch.Tensor:
    """Compute one non-mutating Adam displacement, including bias correction."""
    beta1, beta2 = group["betas"]
    step = float(saved.get("step", 0)) + 1
    previous_m = saved.get("exp_avg", torch.zeros_like(param))
    if reset_momentum:
        previous_m = torch.zeros_like(previous_m)
    previous_v = saved.get("exp_avg_sq", torch.zeros_like(param))
    gradient = grad + group.get("weight_decay", 0) * param.detach()
    if group.get("maximize", False):
        raise ValueError("maximize Adam is outside this audit scope")
    moment = beta1 * previous_m + (1 - beta1) * gradient
    variance = beta2 * previous_v + (1 - beta2) * gradient.square()
    if group.get("amsgrad", False):
        variance = torch.maximum(saved.get("max_exp_avg_sq", torch.zeros_like(param)), variance)
    return (
        -group["lr"]
        * (moment / (1 - beta1**step))
        / ((variance / (1 - beta2**step)).sqrt() + group["eps"])
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    module = importlib.util.spec_from_file_location(
        "support", Path(__file__).with_name("probe_sd_sac_actor_plasticity.py")
    )
    assert module is not None
    assert module.loader is not None
    h = importlib.util.module_from_spec(module)
    module.loader.exec_module(h)
    helper = h.load_helper()
    assert helper.sha(args.checkpoint) == args.expected_sha
    state = helper.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    assert run_fingerprint(spec, Path.cwd()) == state["run_fingerprint"]
    factory = spec.components.model_factory
    assert factory is not None
    model = _instantiate(factory).build()
    model.load_state_dict(state["learner"]["model"], strict=True)
    model.eval().requires_grad_(False)
    model_pin = helper.model_digest(model)
    adam_pin = helper.tree_digest(state["learner"]["actor_optimizer"])
    replay = state["replay_store"]
    size = int(replay["size"])
    episodes = np.unique(replay["episode_codes"][:size])
    rng = np.random.default_rng(17421)
    rng.shuffle(episodes)
    fit_episodes = episodes[: int(0.8 * len(episodes))]
    fit_pool = np.flatnonzero(np.isin(replay["episode_codes"][:size], fit_episodes))
    held_pool = np.flatnonzero(~np.isin(replay["episode_codes"][:size], fit_episodes))
    rows = {
        "fit": rng.choice(fit_pool, min(2048, len(fit_pool)), replace=False),
        "held": rng.choice(held_pool, min(512, len(held_pool)), replace=False),
        "starts": np.flatnonzero(replay["steps"][:size] == 0),
    }
    rows["fit_starts"] = np.intersect1d(fit_pool, rows["starts"])
    rows["held_starts"] = np.intersect1d(held_pool, rows["starts"])
    groups = {}
    for name, selected in rows.items():
        obs = helper.decode_tree(replay["observations"], selected)
        with torch.no_grad():
            qs = [
                0.5 * model.q1(h.indexed(obs, slice(i, i + 128)))
                + 0.5 * model.q2(h.indexed(obs, slice(i, i + 128)))
                for i in range(0, len(selected), 128)
            ]
        behavior = torch.tensor(
            [replay["info"][int(i)]["_trackmaniarl_behavior_entropy"] for i in selected]
        )
        groups[name] = obs, torch.cat(qs), behavior

    options = state["learner"]["sd_sac_options"]
    alpha = max(float(state["learner"]["log_alpha"].exp()), options["entropy_coefficient_min"] or 0)
    if options["entropy_coefficient_max"] is not None:
        alpha = min(alpha, options["entropy_coefficient_max"])
    actor = copy.deepcopy(model.actor).requires_grad_(True)
    actor_pin = helper.model_digest(actor)
    named = list(actor.named_parameters())
    spherical = {id(m.weight) for m in actor.modules() if isinstance(m, HypersphericalLinear)}
    begun = time.monotonic()

    def gradients(group: str) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        obs, q, behavior = groups[group]
        policy = [torch.zeros_like(p) for _, p in named]
        anchor = [torch.zeros_like(p) for _, p in named]
        for i in range(0, len(q), 128):
            if time.monotonic() - begun > 180:
                raise TimeoutError("180s fixed gradient-compute cap")
            sl = slice(i, i + 128)
            logs = actor.log_probabilities(h.indexed(obs, sl))
            entropy = -(logs.exp() * logs).sum(1)
            loss = h.policy_loss(logs, q[sl], alpha, "forward")
            penalty = (
                options["entropy_penalty_coefficient"] * (entropy - behavior[sl]).square().mean()
            )
            pg = torch.autograd.grad(loss, [p for _, p in named], retain_graph=True)
            ag = torch.autograd.grad(penalty, [p for _, p in named])
            weight = len(q[sl]) / len(q)
            for j in range(len(named)):
                policy[j] += pg[j].detach() * weight
                anchor[j] += ag[j].detach() * weight
        return policy, anchor

    def tangent(values: list[torch.Tensor]) -> list[torch.Tensor]:
        result = []
        for g, (_, param) in zip(values, named, strict=True):
            if id(param) in spherical:
                unit = torch.nn.functional.normalize(param.detach(), dim=1)
                g = g - (g * unit).sum(1, keepdim=True) * unit
                assert float((g * unit).sum(1).abs().max()) < 1e-5
            result.append(g)
        return result

    def compare(left: list[torch.Tensor], right: list[torch.Tensor]) -> dict[str, Any]:
        left_flat = torch.cat([g.double().flatten() for g in left])
        r = torch.cat([g.double().flatten() for g in right])
        dot = float(left_flat.dot(r))
        return {
            "left_norm": float(left_flat.norm()),
            "right_norm": float(r.norm()),
            "dot": dot,
            "cosine": dot / max(float(left_flat.norm() * r.norm()), 1e-30),
        }

    saved = {}
    components = {}
    for group in ("fit", "fit_starts", "held", "held_starts"):
        pg, ag = gradients(group)
        total = [p + a for p, a in zip(pg, ag, strict=True)]
        saved[group] = total
        components[group] = compare(pg, ag)
    optimizer = torch.optim.Adam(actor.parameters(), lr=0.0009)
    optimizer.load_state_dict(copy.deepcopy(state["learner"]["actor_optimizer"]))
    parameter_groups = {
        id(param): group for group in optimizer.param_groups for param in group["params"]
    }
    for group in optimizer.param_groups:
        group["lr"] = 0.0009
    obs, _, _ = groups["held_starts"]
    logs = actor.log_probabilities(obs)
    margin_gradients = {}
    initial_margins = {}
    for competitor in (8, 56):
        margin = (logs[:, 35] - logs[:, competitor]).mean()
        initial_margins[str(competitor)] = float(margin.detach())
        margin_gradients[str(competitor)] = [
            g.detach()
            for g in torch.autograd.grad(margin, [param for _, param in named], retain_graph=True)
        ]
    directions = {}
    for scope, grads in (("mixed", saved["fit"]), ("starts", saved["fit_starts"])):
        for mode in ("saved", "fresh", "zero_first_moment"):
            deltas = []
            for (_, param), grad in zip(named, grads, strict=True):
                previous = {} if mode == "fresh" else optimizer.state[param]
                delta = adam_delta(
                    param,
                    grad,
                    previous,
                    parameter_groups[id(param)],
                    reset_momentum=mode == "zero_first_moment",
                )
                assert torch.isfinite(delta).all()
                deltas.append(delta)
            projected = tangent(deltas)
            directions[scope + "/" + mode] = {
                "raw_norm": compare(deltas, deltas)["left_norm"],
                "tangent_norm": compare(projected, projected)["left_norm"],
                "held_start_loss_derivative": compare(saved["held_starts"], projected)["dot"],
                "held_general_loss_derivative": compare(saved["held"], projected)["dot"],
                "target35_log_probability_margin_derivatives": {
                    key: compare(gradient, projected)["dot"]
                    for key, gradient in margin_gradients.items()
                },
            }
    comparisons = directions
    assert helper.sha(args.checkpoint) == args.expected_sha
    assert helper.model_digest(model) == model_pin
    assert helper.model_digest(actor) == actor_pin
    assert helper.tree_digest(state["learner"]["actor_optimizer"]) == adam_pin
    report = {
        "status": "COMPLETE",
        "checkpoint_sha256": args.expected_sha,
        "original_model_adam_checkpoint_unchanged": True,
        "runtime_learner_updates": 0,
        "optimizer_steps": 0,
        "controller_created": False,
        "cpu_threads": 1,
        "priority": "IDLE",
        "alpha": alpha,
        "elapsed_seconds": time.monotonic() - begun,
        "cap_seconds": 180,
        "rows": {name: selected.tolist() for name, selected in rows.items()},
        "policy_vs_anchor": components,
        "comparisons": comparisons,
        "initial_target35_log_probability_margins": initial_margins,
        "limitation": (
            "Analytic one-step Adam directions at the saved actor; no optimizer step was executed. "
            "finite-step interference, critic correctness or driving evidence."
        ),
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "elapsed_seconds": report["elapsed_seconds"],
                "comparisons": comparisons,
            }
        )
    )


if __name__ == "__main__":
    main()
