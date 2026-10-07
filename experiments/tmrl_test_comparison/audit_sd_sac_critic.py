"""CPU-only saved-checkpoint inference; never creates a learner or game controller.

Run this file with PYTHONPATH pointing at the checkpoint's frozen runtime.
Recorded behavior returns are off-policy proxies, not current-policy ground truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["WANDB_MODE"] = "disabled"

import numpy as np
import psutil  # type: ignore[import-untyped]
import torch
import zstandard

from trackmaniarl.algorithms.sd_sac_objectives import categorical_statistics
from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec


def recorded_returns(replay: dict[str, Any], *, gamma: float, alpha: float) -> np.ndarray:
    """Return [raw, soft, horizon] for recorded terminal suffixes; NaN otherwise.

    Explicit links and episode/step checks prevent crossing gaps or episode resets.
    Soft Q excludes the entropy of the action already selected at the current state.
    """
    size = int(replay["size"])
    first = int(replay["next_index"]) - size
    result = np.full((size, 3), np.nan, dtype=np.float64)
    for row in range(size - 1, -1, -1):
        if replay["truncated"][row]:
            continue
        reward = float(replay["rewards"][row])
        if replay["terminated"][row]:
            result[row] = reward, reward, 1
            continue
        following = int(replay["next_ids"][row]) - first
        if not row < following < size:
            continue
        if (
            replay["episode_codes"][row] != replay["episode_codes"][following]
            or replay["steps"][following] != replay["steps"][row] + 1
            or not np.isfinite(result[following]).all()
        ):
            continue
        info = replay["info"].get(first + following, {})
        entropy = info.get("_trackmaniarl_behavior_entropy")
        if entropy is None or not math.isfinite(entropy) or entropy < 0:
            continue
        raw, soft, horizon = result[following]
        result[row] = reward + gamma * raw, reward + gamma * (soft + alpha * entropy), horizon + 1
    return result


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_checkpoint(path: Path, *, temporary_directory: Path) -> dict[str, Any]:
    with path.open("rb") as stream, tempfile.TemporaryFile(dir=temporary_directory) as temp:
        compressed = stream.read(4) == b"\x28\xb5\x2f\xfd"
        stream.seek(0)
        if compressed:
            with zstandard.ZstdDecompressor().stream_reader(stream) as reader:
                shutil.copyfileobj(reader, temp)
        else:
            shutil.copyfileobj(stream, temp)
        temp.seek(0)
        return cast(dict[str, Any], torch.load(temp, map_location="cpu", weights_only=False))


def decode_tree(tree: dict[str, Any], rows: np.ndarray) -> Any:
    def decode(spec: Any) -> Any:
        if spec[0] == "leaf":
            return torch.as_tensor(np.array(tree["arrays"][spec[1]][rows], copy=True))
        if spec[0] == "mapping":
            return {key: decode(child) for key, child in zip(spec[1], spec[2], strict=True)}
        values = [decode(child) for child in spec[1]]
        return tuple(values) if spec[0] == "tuple" else values

    return decode(tree["spec"])


def summary(values: Any) -> dict[str, float | int]:
    array = np.asarray(values, dtype=np.float64)
    if not np.isfinite(array).all():
        raise ValueError("Non-finite audit measurement")
    if not array.size:
        return {"count": 0}
    return {
        "count": int(array.size),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "p95": float(np.quantile(array, 0.95)),
        "min": float(array.min()),
        "max": float(array.max()),
    }


def model_digest(model: Any) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        digest.update(name.encode())
        digest.update(value.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def infer(models: tuple[Any, Any], replay: dict[str, Any], rows: np.ndarray) -> dict[str, Any]:
    model, target = models
    output: dict[str, list[Any]] = {
        name: [] for name in ("q", "next_value", "entropy", "pair_agreement", "gap", "regret")
    }
    first = int(replay["next_index"]) - int(replay["size"])
    with torch.inference_mode():
        for chunk in np.array_split(rows, max(1, math.ceil(len(rows) / 64))):
            observations = decode_tree(replay["observations"], chunk)
            actions = decode_tree(replay["actions"], chunk).long().reshape(-1, 1)
            q1, q2 = model.q1(observations), model.q2(observations)
            q = 0.5 * (q1 + q2)
            probabilities, logs = categorical_statistics(model.actor, observations)
            output["q"].extend(q.gather(1, actions).squeeze(1).tolist())
            output["entropy"].extend((-(probabilities * logs).sum(1)).tolist())
            output["pair_agreement"].extend((q1.argmax(1) == q2.argmax(1)).tolist())
            top = q.topk(2, dim=1).values
            output["gap"].extend((top[:, 0] - top[:, 1]).tolist())
            greedy = probabilities.argmax(1, keepdim=True)
            output["regret"].extend((q.max(1).values - q.gather(1, greedy).squeeze(1)).tolist())
            # Terminal continuation is zero. Nonterminal rows must have a validated next link.
            following = np.asarray(replay["next_ids"])[chunk] - first
            following = np.where(np.asarray(replay["terminated"])[chunk], chunk, following)
            next_obs = decode_tree(replay["observations"], following)
            next_p, next_logs = categorical_statistics(model.actor, next_obs)
            next_q = 0.5 * (target.q1(next_obs) + target.q2(next_obs))
            output["next_value"].extend(
                torch.stack(((next_p * next_q).sum(1), -(next_p * next_logs).sum(1)), 1).tolist()
            )
    return {name: np.asarray(values) for name, values in output.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    if torch.cuda.is_available():
        raise RuntimeError("Audit must be CPU-only")
    started = datetime.now(UTC)
    before_sha = sha(args.checkpoint)
    print("Loading copied checkpoint on CPU", flush=True)
    state = read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    if spec.training.n_step != 1:
        raise ValueError("Audit supports the SD-SAC one-step contract only")
    fingerprint = run_fingerprint(spec, Path.cwd())
    # Fail closed before inference if the supplied source differs from the checkpoint.
    if state["run_fingerprint"] != fingerprint:
        raise ValueError("Audit runtime/config fingerprint differs from checkpoint")
    factory = spec.components.model_factory
    if factory is None:
        raise ValueError("Checkpoint audit requires a model factory")
    model = _instantiate(factory).build()
    target = _instantiate(factory).build()
    model.load_state_dict(state["learner"]["model"], strict=True)
    target.load_state_dict(state["learner"]["target_model"], strict=True)
    for item in (model, target):
        item.eval().requires_grad_(False)
    initial_digests = [model_digest(item) for item in (model, target)]
    options = state["learner"]["sd_sac_options"]
    alpha = float(state["learner"]["log_alpha"].exp())
    alpha = max(alpha, options["entropy_coefficient_min"] or 0)
    if options["entropy_coefficient_max"] is not None:
        alpha = min(alpha, options["entropy_coefficient_max"])
    replay = state["replay_store"]
    size = int(replay["size"])
    first = int(replay["next_index"]) - size
    indices = np.arange(size)
    following = np.asarray(replay["next_ids"]) - first
    bounded = np.clip(following, 0, size - 1)
    linked = (
        (following > indices)
        & (following < size)
        & (replay["episode_codes"] == replay["episode_codes"][bounded])
        & (replay["steps"][bounded] == replay["steps"] + 1)
    )
    terminals = np.flatnonzero(replay["terminated"] & ~replay["truncated"])
    pool = np.flatnonzero(linked & ~replay["terminated"] & ~replay["truncated"])
    seed = 17421
    rows = np.r_[terminals, np.random.default_rng(seed).choice(pool, min(1024, len(pool)), False)]
    print(
        f"Inference on {len(terminals)} terminals and {len(rows) - len(terminals)} others",
        flush=True,
    )
    measured = infer((model, target), replay, rows)
    q = measured["q"]
    terminal = replay["terminated"][rows]
    rewards = replay["rewards"][rows]
    continuation = measured["next_value"][:, 0] + alpha * measured["next_value"][:, 1]
    bellman = rewards + spec.training.gamma * np.where(terminal, 0, continuation)
    returns = recorded_returns(replay, gamma=spec.training.gamma, alpha=alpha)[rows]
    groups = {}
    for name, mask in {
        "terminal": terminal,
        "nonterminal": ~terminal,
        "last_20_steps": (~terminal) & (returns[:, 2] <= 20),
        "more_than_20_steps": returns[:, 2] > 20,
    }.items():
        mask = mask & np.isfinite(returns).all(1)
        groups[name] = {
            "q": summary(q[mask]),
            "behavior_soft_return_proxy": summary(returns[mask, 1]),
            "proxy_bias": summary(q[mask] - returns[mask, 1]),
            "proxy_abs_error": summary(np.abs(q[mask] - returns[mask, 1])),
            "bellman_abs_error": summary(np.abs(q[mask] - bellman[mask])),
        }
    if initial_digests != [model_digest(item) for item in (model, target)]:
        raise RuntimeError("Inference changed model tensors")
    if before_sha != sha(args.checkpoint):
        raise RuntimeError("Copied checkpoint changed")
    report = {
        "started": started.isoformat(),
        "finished": datetime.now(UTC).isoformat(),
        "runtime": str(Path.cwd()),
        "runtime_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": before_sha,
        "audit_script_sha256": sha(Path(__file__)),
        "config_sha256": sha(args.config),
        "fingerprint": fingerprint,
        "checkpoint_transitions": state["distributed"]["transitions"],
        "checkpoint_updates": state["distributed"]["updates"],
        "replay_size": size,
        "seed": seed,
        "sampled_transition_ids": (rows + first).tolist(),
        "all_terminal_count": len(terminals),
        "nonterminal_sample_count": len(rows) - len(terminals),
        "nonterminal_samples_without_recorded_terminal_suffix": int(
            ((~terminal) & ~np.isfinite(returns).all(1)).sum()
        ),
        "alpha": alpha,
        "gamma": spec.training.gamma,
        "groups": groups,
        "policy_entropy": summary(measured["entropy"]),
        "critic_pair_greedy_agreement": float(measured["pair_agreement"].mean()),
        "critic_top_gap": summary(measured["gap"]),
        "actor_q_regret": summary(measured["regret"]),
        "bellman_abs_error_all_sampled": summary(np.abs(q - bellman)),
        "cpu_threads": 1,
        "learner_updates": 0,
        "controller_created": False,
        "checkpoint_unchanged": True,
        "model_tensors_unchanged": True,
        "limitations": [
            "Replay was already used in training; this is not a held-out generalization test.",
            "Historical stochastic behavior differs from the current policy and greedy evaluation.",
            "Behavior soft returns use the checkpoint alpha throughout recorded terminal suffixes.",
            "Bellman agreement is self-consistency, not independently correct action rankings.",
            "No counterfactual unchosen-action values or driving qualification are established.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    print("Audit saved", flush=True)


if __name__ == "__main__":
    main()
