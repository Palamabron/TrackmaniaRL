"""Inspect critic feature and linear-head geometry without updates."""

from __future__ import annotations

import argparse
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
    optimizer_pin = helper.tree_digest(
        {k: v for k, v in state["learner"].items() if "optimizer" in k}
    )
    rng = np.random.default_rng(17421)
    nonterminal = np.flatnonzero(~np.asarray(replay["terminated"][:size], dtype=bool))
    rows = {
        "nonterminal": rng.choice(nonterminal, min(1024, len(nonterminal)), replace=False),
        "terminal": np.flatnonzero(replay["terminated"][:size]),
        "starts": np.flatnonzero(replay["steps"][:size] == 0),
    }
    begun = time.monotonic()

    def summary(value: torch.Tensor) -> dict[str, Any]:
        v = value.detach().double().flatten()
        return {
            "count": len(v),
            "mean": float(v.mean()),
            "quantiles": torch.quantile(
                v, torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0], dtype=v.dtype)
            ).tolist(),
        }

    result = {}
    with torch.no_grad():
        for critic_name in ("q1", "q2"):
            critic = getattr(model, critic_name)
            assert len(critic) == 2
            assert isinstance(critic[1], torch.nn.Linear)
            encoder, head = critic[0], critic[1]
            weight, bias = head.weight.double(), head.bias.double()
            norms = weight.norm(dim=1)
            entry = {"head_weight_norm": summary(norms), "head_bias": summary(bias), "groups": {}}
            for group, selected in rows.items():
                if time.monotonic() - begun > 180:
                    raise TimeoutError("180s fixed geometry cap")
                obs = helper.decode_tree(replay["observations"], selected)
                features = torch.cat(
                    [
                        encoder(h.indexed(obs, slice(i, i + 128)))
                        for i in range(0, len(selected), 128)
                    ]
                ).double()
                q = features @ weight.T + bias
                expected = torch.cat(
                    [
                        critic(h.indexed(obs, slice(i, i + 128)))
                        for i in range(0, len(selected), 128)
                    ]
                ).double()
                assert torch.allclose(q, expected, atol=1e-5, rtol=1e-5)
                lengths = features.norm(dim=1)
                radius = lengths[:, None] * norms[None, :]
                centered = q - bias
                assert bool((centered.abs() <= radius + 1e-8).all())
                alignment = centered / radius.clamp_min(1e-30)
                directions = features / lengths[:, None].clamp_min(1e-30)
                centroid = directions.mean(0)
                covariance_features = features - features.mean(0)
                singular = torch.linalg.svdvals(covariance_features)
                energy = singular.square()
                fractions = energy / energy.sum().clamp_min(1e-30)
                positive = fractions[fractions > 0]
                effective_rank = float((-(positive * positive.log()).sum()).exp())
                actions = torch.as_tensor(
                    helper.decode_tree(replay["actions"], selected), dtype=torch.long
                ).flatten()
                taken = q.gather(1, actions[:, None])[:, 0]
                observed_norm_bound = float(lengths.max())
                lower = bias - observed_norm_bound * norms
                upper = bias + observed_norm_bound * norms
                rewards = torch.as_tensor(
                    np.asarray(replay["rewards"])[selected], dtype=torch.float64
                )
                target_outside = (rewards < lower[actions]) | (rewards > upper[actions])
                entry["groups"][group] = {
                    "feature_norm": summary(lengths),
                    "direction_centroid_norm": float(centroid.norm()),
                    "mean_pairwise_cosine_including_self": float(centroid.square().sum()),
                    "centered_feature_variance_trace": float(energy.sum() / len(features)),
                    "centered_effective_rank": effective_rank,
                    "top_pc_variance_fraction": float(fractions.max()),
                    "head_alignment_all_actions": summary(alignment),
                    "taken_q": summary(taken),
                    "q_action_span": summary(q.max(1).values - q.min(1).values),
                    "observed_norm_envelope_lower": summary(lower),
                    "observed_norm_envelope_upper": summary(upper),
                    "terminal_reward_outside_observed_norm_envelope_fraction": (
                        float(target_outside.double().mean()) if group == "terminal" else None
                    ),
                    "taken_head_alignment": summary(alignment.gather(1, actions[:, None])[:, 0]),
                    "rows": selected.tolist(),
                }
            result[critic_name] = entry
    assert helper.sha(args.checkpoint) == args.expected_sha
    assert helper.model_digest(model) == model_pin
    assert helper.tree_digest(state["learner"]["actor_optimizer"]) == adam_pin
    assert (
        helper.tree_digest({k: v for k, v in state["learner"].items() if "optimizer" in k})
        == optimizer_pin
    )
    report = {
        "status": "COMPLETE",
        "checkpoint_sha256": args.expected_sha,
        "fingerprint": state["run_fingerprint"],
        "original_model_all_optimizers_unchanged": True,
        "optimizer_steps": 0,
        "controller_created": False,
        "cpu_threads": 1,
        "priority": "IDLE",
        "elapsed_seconds": time.monotonic() - begun,
        "critics": result,
        "limitations": [
            "Observed norm envelope is not a global encoder bound or capacity proof.",
            "Current/predecessor use different replay populations; no paired causal claim.",
            "Feature concentration and rank are descriptive; failure causality is unproven.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "COMPLETE",
                "elapsed_seconds": report["elapsed_seconds"],
                "critics": {
                    k: {
                        g: {n: v for n, v in z.items() if n not in ("rows",)}
                        for g, z in x["groups"].items()
                    }
                    for k, x in result.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
