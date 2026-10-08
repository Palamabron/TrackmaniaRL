"""Compare sharp-then-original actor targets with an equal-step ordinary control."""

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
from trackmaniarl.models.backbones import project_hyperspherical_weights


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--adam-state", choices=("saved", "fresh"), default="saved")
    parser.add_argument("--fit-scope", choices=("mixed", "starts", "mixture"), default="mixture")
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    if args.fit_scope == "mixture" and args.baseline is None:
        parser.error("mixture requires completed ordinary-mixed baseline")
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
    if args.fit_scope in ("starts", "mixture"):
        rows["fit_starts"] = np.intersect1d(fit_pool, rows["starts"])
        rows["held_starts"] = np.intersect1d(held_pool, rows["starts"])
        assert len(rows["fit_starts"])
        assert len(rows["held_starts"])
        assert not np.intersect1d(rows["fit_starts"], rows["held_starts"]).size
    if args.fit_scope == "starts":
        rows["fit"] = rows.pop("fit_starts")
    assert args.fit_scope == "mixture"
    assert args.adam_state == "saved"
    variants = [("ordinary", 0.0009, 1.0), ("sharp_then_original", 0.0009, 0.1)]
    cap_seconds = 300
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

    def metrics(actor: Any) -> dict[str, Any]:
        result = {}
        with torch.no_grad():
            for name, (obs, q, _) in groups.items():
                logs = torch.cat(
                    [
                        actor.log_probabilities(h.indexed(obs, slice(i, i + 128)))
                        for i in range(0, len(q), 128)
                    ]
                )
                greedy = logs.argmax(1)
                target_logs = torch.log_softmax(q / alpha, dim=1)
                result[name] = {
                    "agreement": float((greedy == q.argmax(1)).float().mean()),
                    "regret": float((q.max(1).values - q.gather(1, greedy[:, None])[:, 0]).mean()),
                    "forward_kl": float((target_logs.exp() * (target_logs - logs)).sum(1).mean()),
                    "reverse_kl": float((logs.exp() * (logs - target_logs)).sum(1).mean()),
                    "expected_q": float((logs.exp() * q).sum(1).mean()),
                    "sac_objective": float(h.policy_loss(logs, q, alpha, "sac")),
                    "entropy": float(-(logs.exp() * logs).sum(1).mean()),
                    "greedy_actions": greedy.tolist(),
                    "greedy_regret_per_row": (
                        q.max(1).values - q.gather(1, greedy[:, None])[:, 0]
                    ).tolist(),
                }
        return result

    options = state["learner"]["sd_sac_options"]
    alpha = max(float(state["learner"]["log_alpha"].exp()), options["entropy_coefficient_min"] or 0)
    if options["entropy_coefficient_max"] is not None:
        alpha = min(alpha, options["entropy_coefficient_max"])
    report = {
        "checkpoint_sha256": args.expected_sha,
        "alpha": alpha,
        "adam_state": args.adam_state,
        "fit_scope": args.fit_scope,
        "schedules": [name for name, _, _ in variants],
        "actor_target_alpha_schedule": [alpha * 0.1, alpha],
        "critic_and_saved_alpha": alpha,
        "auxiliary_scope": "fixed two-stage distillation; ordinary rows; no start sampling",
        "design": {
            "objectives": sorted({objective for objective, _, _ in variants}),
            "learning_rates": sorted({lr for _, lr, _ in variants}),
            "seeds": [17, 29],
            "steps_per_copy": 128,
            "cap_seconds": cap_seconds,
            "targets": (
                "frozen meanQ; ordinary128 vs sharp64/original64; unchanged anchor/critic alpha"
            ),
            "projection": "after each disposable saved-Adam actor step",
        },
        "cpu_threads": 1,
        "priority": "IDLE",
        "runtime_learner_updates": 0,
        "controller_created": False,
        "rows": {name: selected.tolist() for name, selected in rows.items()},
        "baseline": metrics(model.actor),
        "results": [],
        "status": "RUNNING",
        "limitation": "Fixed saved Q and replay-used held episodes; "
        "no critic correctness or driving claim.",
    }
    begun = time.monotonic()
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for objective, lr, fraction in variants:
        for seed in (17, 29):
            actor = copy.deepcopy(model.actor).requires_grad_(True)
            optimizer = torch.optim.Adam(actor.parameters(), lr=lr)
            if args.adam_state == "saved":
                optimizer.load_state_dict(copy.deepcopy(state["learner"]["actor_optimizer"]))
            for group in optimizer.param_groups:
                group["lr"] = lr
            sample = np.random.default_rng(seed)
            obs, q, behavior = groups["fit"]
            midpoint = {}
            for copy_step in range(128):
                if time.monotonic() - begun > cap_seconds:
                    raise TimeoutError(f"{cap_seconds}s offline cap")
                index = sample.integers(0, len(q), 128)
                logs = actor.log_probabilities(h.indexed(obs, index))
                entropy = -(logs.exp() * logs).sum(1)
                loss = h.policy_loss(
                    logs, q[index], alpha * (fraction if copy_step < 64 else 1.0), "forward"
                )
                loss += (
                    options["entropy_penalty_coefficient"]
                    * (entropy - behavior[index]).square().mean()
                )
                assert torch.isfinite(loss)
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
                project_hyperspherical_weights(actor)
                if copy_step == 63:
                    midpoint = metrics(actor)
            report["results"].append(
                {
                    "objective": objective,
                    "schedule": objective,
                    "lr": lr,
                    "seed": seed,
                    "copy_steps": 128,
                    "midpoint_metrics": midpoint,
                    "metrics": metrics(actor),
                }
            )
            args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(
                f"Completed disposable actor objective={objective} lr={lr} seed={seed}", flush=True
            )
    if args.fit_scope == "mixture":
        baseline = json.loads(args.baseline.read_text())
        assert baseline["status"] == "COMPLETE"
        assert baseline["checkpoint_sha256"] == args.expected_sha
        assert baseline["rows"]["fit"] == rows["fit"].tolist()
        assert baseline["rows"]["held"] == rows["held"].tolist()
        assert baseline.get("adam_state", "saved") == "saved"
        sharp_reference = json.loads(
            (args.output.parent / "actor-target-sharpening.json").read_text()
        )
        comparison = []
        for result in report["results"]:
            source = baseline if result["schedule"] == "ordinary" else sharp_reference
            midpoint_reference = next(
                item
                for item in source["results"]
                if item["seed"] == result["seed"]
                and item["lr"] == 0.0009
                and item["objective"] == "forward"
            )
            for name in ("forward_kl", "reverse_kl", "regret", "agreement"):
                assert (
                    abs(
                        result["midpoint_metrics"]["held"][name]
                        - midpoint_reference["metrics"]["held"][name]
                    )
                    < 1e-6
                )
            if result["schedule"] == "ordinary":
                continue
            matched = next(
                item
                for item in report["results"]
                if item["seed"] == result["seed"] and item["schedule"] == "ordinary"
            )
            prior = next(
                item
                for item in baseline["results"]
                if item["seed"] == result["seed"]
                and item["lr"] == 0.0009
                and item["objective"] == "forward"
            )
            checks = {
                reference_name: {
                    name: result["metrics"]["held"][name]
                    <= 1.2 * reference["metrics"]["held"][name]
                    for name in ("forward_kl", "reverse_kl", "regret")
                }
                for reference_name, reference in (("matched128", matched), ("prior64", prior))
            }
            comparison.append(
                {
                    "seed": result["seed"],
                    "guards": checks,
                    "held_start_agreement": result["metrics"]["held_starts"]["agreement"],
                    "all_guards_pass": all(all(c.values()) for c in checks.values()),
                }
            )
        report["comparison"] = comparison
        report["eligible_schedule"] = all(
            item["all_guards_pass"] and item["held_start_agreement"] == 1 for item in comparison
        )
        assert len(comparison) == 2
    assert helper.sha(args.checkpoint) == args.expected_sha
    assert helper.model_digest(model) == model_pin
    assert helper.tree_digest(state["learner"]["actor_optimizer"]) == adam_pin
    report.update(
        status="COMPLETE",
        saved_model_adam_checkpoint_unchanged=True,
        total_copy_optimizer_steps=len(variants) * 2 * 128,
        elapsed_seconds=time.monotonic() - begun,
    )
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
