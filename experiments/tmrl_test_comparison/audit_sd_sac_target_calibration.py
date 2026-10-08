"""CPU-only, zero-update inspection of saved SD-SAC target and clipping geometry."""

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
from trackmaniarl.trackmania.actions import build_brake_tap_action_table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("checkpoint", "config", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    support = importlib.util.spec_from_file_location(
        "audit_support", Path(__file__).with_name("audit_sd_sac_critic.py")
    )
    assert support is not None
    assert support.loader is not None
    h = importlib.util.module_from_spec(support)
    support.loader.exec_module(h)
    if h.sha(args.checkpoint) != args.expected_sha:
        raise ValueError("Checkpoint SHA mismatch")
    state = h.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    if run_fingerprint(spec, Path.cwd()) != state["run_fingerprint"]:
        raise ValueError("Runtime/config fingerprint mismatch")
    if spec.training.n_step != 1:
        raise ValueError("One-step checkpoint required")
    factory = spec.components.model_factory
    assert factory is not None
    model, target = [_instantiate(factory).build() for _ in range(2)]
    for item, key in ((model, "model"), (target, "target_model")):
        item.load_state_dict(state["learner"][key], strict=True)
        item.eval().requires_grad_(False)
    pins = [h.model_digest(item) for item in (model, target)]
    options = state["learner"]["sd_sac_options"]
    alpha = max(float(state["learner"]["log_alpha"].exp()), options["entropy_coefficient_min"] or 0)
    if options["entropy_coefficient_max"] is not None:
        alpha = min(alpha, options["entropy_coefficient_max"])
    epsilon = options["q_clip_epsilon"]
    replay = state["replay_store"]
    size = int(replay["size"])
    first = int(replay["next_index"]) - size
    index = np.arange(size)
    following = np.asarray(replay["next_ids"])[:size] - first
    bounded = np.clip(following, 0, size - 1)
    terminated = np.asarray(replay["terminated"])[:size]
    truncated = np.asarray(replay["truncated"])[:size]
    linked = (
        (following > index)
        & (following < size)
        & (replay["episode_codes"][:size] == replay["episode_codes"][bounded])
        & (replay["steps"][bounded] == replay["steps"][:size] + 1)
    )
    terminals = np.flatnonzero(terminated & ~truncated)
    pool = np.flatnonzero(linked & ~terminated & ~truncated)
    rows = np.r_[terminals, np.random.default_rng(17421).choice(pool, min(1024, len(pool)), False)]
    values: dict[str, list[Any]] = {}

    def save(name: str, tensor: torch.Tensor) -> None:
        values.setdefault(name, []).extend(tensor.tolist())

    with torch.inference_mode():
        for chunk in np.array_split(rows, max(1, int(np.ceil(len(rows) / 64)))):
            obs = h.decode_tree(replay["observations"], chunk)
            next_rows = np.where(terminated[chunk], chunk, following[chunk])
            nxt = h.decode_tree(replay["observations"], next_rows)
            actions = h.decode_tree(replay["actions"], chunk).long().reshape(-1, 1)
            q1, q2 = model.q1(obs), model.q2(obs)
            t1, t2 = target.q1(obs), target.q2(obs)
            n1, n2 = target.q1(nxt), target.q2(nxt)
            logs = model.actor.log_probabilities(nxt)
            probs = logs.exp()
            entropy = -(probs * logs).sum(1)
            reward = torch.as_tensor(replay["rewards"][chunk])
            discount = spec.training.gamma * torch.as_tensor(~terminated[chunk])
            avg_value = (probs * ((n1 + n2) / 2)).sum(1)
            min_value = (probs * torch.minimum(n1, n2)).sum(1)
            avg_target = reward + discount * (avg_value + alpha * entropy)
            min_target = reward + discount * (min_value + alpha * entropy)
            save("reward", reward)
            save("entropy_bootstrap", discount * alpha * entropy)
            save("mean_minus_min_target", avg_target - min_target)
            save("target_mean", avg_target)
            save("target_min", min_target)
            for name, current, old in (("q1", q1, t1), ("q2", q2, t2)):
                current = current.gather(1, actions).flatten()
                old = old.gather(1, actions).flatten()
                clipped = old + (current - old).clamp(-epsilon, epsilon)
                blocked = ((current - old).abs() > epsilon) & (
                    (clipped - avg_target).square() > (current - avg_target).square()
                )
                save(name + "_current", current)
                save(name + "_target_lag", (current - old).abs())
                save(name + "_clip_blocked", blocked.float())
                save(name + "_td_mean_abs", (current - avg_target).abs())
                save(name + "_td_min_abs", (current - min_target).abs())
    measured = {key: np.asarray(value) for key, value in values.items()}
    groups = {}
    for name, mask in (("terminal", terminated[rows]), ("nonterminal", ~terminated[rows])):
        groups[name] = {key: h.summary(value[mask]) for key, value in measured.items()}

    starts = np.flatnonzero(replay["steps"][:size] == 0)
    _, controls = build_brake_tap_action_table()
    gas = torch.tensor([control[0] for control in controls])
    starts_report = {}
    with torch.inference_mode():
        obs = h.decode_tree(replay["observations"], starts)
        q1, q2 = model.q1(obs), model.q2(obs)
        for name, q in (("mean", (q1 + q2) / 2), ("minimum", torch.minimum(q1, q2))):
            if q.shape[1] != len(controls):
                raise ValueError("Action table mismatch")
            greedy = q.argmax(1)
            unique, counts = greedy.unique(return_counts=True)
            soft = torch.softmax(q / alpha, 1)
            starts_report[name] = {
                "top_action_counts": dict(zip(unique.tolist(), counts.tolist(), strict=True)),
                "top_action_gas_mean": float(gas[greedy].mean()),
                "soft_target_gas_mass": h.summary((soft * gas).sum(1).numpy()),
                "best_gas_minus_best_no_gas": h.summary(
                    (q[:, gas > 0].max(1).values - q[:, gas == 0].max(1).values).numpy()
                ),
                "entropy": h.summary((-(soft * soft.clamp_min(1e-30).log()).sum(1)).numpy()),
            }
    assert pins == [h.model_digest(item) for item in (model, target)]
    assert h.sha(args.checkpoint) == args.expected_sha
    report = {
        "checkpoint_sha256": args.expected_sha,
        "fingerprint": state["run_fingerprint"],
        "alpha": alpha,
        "q_clip_epsilon": epsilon,
        "sampled_transition_ids": (rows + first).tolist(),
        "groups": groups,
        "starts": starts_report,
        "initial_observations": len(starts),
        "cpu_threads": 1,
        "priority": "IDLE",
        "optimizer_steps": 0,
        "controller_created": False,
        "checkpoint_and_models_unchanged": True,
        "limitations": [
            "Saved replay is not independent evaluation data.",
            "Mean/min counterfactual targets are not learned policies or true action values.",
            "Truncated rows are excluded; terminal continuation is zero.",
            "Clipping geometry describes this checkpoint, not historical training gradients.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print("Target calibration audit saved")


if __name__ == "__main__":
    main()
