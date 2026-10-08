"""Audit frozen target geometry and distribution-error decomposition; zero updates."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
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
    audit = {}
    for name in ("held", "held_starts"):
        _, q, behavior = groups[name]
        q = q.double()
        target = torch.log_softmax(q / alpha, dim=1)
        sharp = torch.log_softmax(q / (alpha * 0.1), dim=1)
        restored = torch.log_softmax(sharp * 0.1, dim=1)
        assert torch.allclose(restored, target, atol=1e-10, rtol=1e-10)
        entropy = float(-(target.exp() * target).sum(1).mean())
        soft_value = float((alpha * torch.logsumexp(q / alpha, dim=1)).mean())
        top = torch.topk(q, 2, dim=1).values
        audit[name] = {
            "target_entropy": entropy,
            "sharp_target_entropy": float(-(sharp.exp() * sharp).sum(1).mean()),
            "target_expected_q": float((target.exp() * q).sum(1).mean()),
            "soft_value": soft_value,
            "behavior_entropy_mean": float(behavior.mean()),
            "q_top2_gap_quantiles": torch.quantile(
                top[:, 0] - top[:, 1], torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0], dtype=q.dtype)
            ).tolist(),
            "target_top_probability_quantiles": torch.quantile(
                target.exp().max(1).values, torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0], dtype=q.dtype)
            ).tolist(),
            "ideal_sharp_forward_kl_original": float(
                (target.exp() * (target - sharp)).sum(1).mean()
            ),
            "ideal_sharp_reverse_kl_original": float(
                (sharp.exp() * (sharp - target)).sum(1).mean()
            ),
            "ideal_compensation_max_log_error": float((restored - target).abs().max()),
        }
    reports: dict[str, list[dict[str, Any]]] = {}
    for filename in (
        "actor-objectives.json",
        "actor-target-sharpening.json",
        "temperature-compensation.json",
    ):
        source = json.loads((args.output.parent / filename).read_text())
        assert source["status"] == "COMPLETE"
        assert source["checkpoint_sha256"] == args.expected_sha
        assert source["rows"]["held"] == rows["held"].tolist()
        reports[filename] = []
        for result in source["results"]:
            if result["objective"] != "forward" or result["lr"] != 0.0009:
                continue
            item = {"seed": result["seed"], "groups": {}}
            for name in ("held", "held_starts"):
                if name not in result["metrics"]:
                    continue
                m = result["metrics"][name]
                d = audit[name]
                reconstructed = (d["soft_value"] - m["expected_q"]) / alpha - m["entropy"]
                assert abs(reconstructed - m["reverse_kl"]) < 2e-4
                item["groups"][name] = {
                    "actor_entropy": m["entropy"],
                    "entropy_minus_target": m["entropy"] - d["target_entropy"],
                    "target_to_actor_cross_entropy": m["forward_kl"] + d["target_entropy"],
                    "expected_q_minus_target": m["expected_q"] - d["target_expected_q"],
                    "reverse_kl_reconstructed": reconstructed,
                    "forward_kl": m["forward_kl"],
                    "reverse_kl": m["reverse_kl"],
                    "agreement": m["agreement"],
                    "regret": m["regret"],
                }
            reports[filename].append(item)
    assert helper.sha(args.checkpoint) == args.expected_sha
    assert helper.model_digest(model) == model_pin
    assert helper.tree_digest(state["learner"]["actor_optimizer"]) == adam_pin
    report = {
        "status": "COMPLETE",
        "checkpoint_sha256": args.expected_sha,
        "original_model_adam_unchanged": True,
        "optimizer_steps": 0,
        "runtime_updates": 0,
        "controller_created": False,
        "cpu_threads": 1,
        "priority": "IDLE",
        "alpha": alpha,
        "rows": {k: v.tolist() for k, v in rows.items()},
        "target_geometry": audit,
        "decomposition": reports,
        "limitation": (
            "Frozen Q is not ground truth. Disposable trained logits were not persisted; "
            "aggregate identities only, not per-row trained errors."
        ),
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"target_geometry": audit, "decomposition": reports}, indent=2))


if __name__ == "__main__":
    main()
