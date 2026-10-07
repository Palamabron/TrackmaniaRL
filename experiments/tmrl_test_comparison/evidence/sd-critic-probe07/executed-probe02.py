"""Bounded CPU regression on disposable critics; never runs a learner/controller.

Use the checkpoint's frozen runtime first in PYTHONPATH. Evaluation episodes are
excluded from this probe's optimization, but were used in original live training.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["WANDB_MODE"] = "disabled"

import numpy as np
import psutil  # type: ignore[import-untyped]
import torch

if __package__:
    from .audit_sd_sac_critic import decode_tree, model_digest, read_checkpoint, sha
else:
    # Import this adjacent helper without adding editable experiment packages to
    # the frozen runtime's component-source fingerprint.
    from audit_sd_sac_critic import decode_tree, model_digest, read_checkpoint, sha
from trackmaniarl.algorithms.sac_support import SACBatch, discrete_batch
from trackmaniarl.algorithms.stable_discrete_soft_actor_critic import StableDiscreteSoftActorCritic
from trackmaniarl.core.data import BatchRequest, TrainingBatch
from trackmaniarl.core.fingerprint import run_fingerprint
from trackmaniarl.core.pytree import tree_collate, tree_map
from trackmaniarl.core.replay import InMemoryReplayStore
from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec


def split_episodes(codes: np.ndarray, *, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Split whole episodes, including all their terminal and preceding rows."""
    unique = np.unique(codes)
    if len(unique) < 5:
        raise ValueError("At least five episodes required")
    shuffled = np.random.default_rng(seed).permutation(unique)
    held = shuffled[: max(1, len(unique) // 5)]
    mask = np.isin(codes, held)
    return np.flatnonzero(~mask), np.flatnonzero(mask)


def class_weights(terminal: np.ndarray, p: float, q: float) -> np.ndarray:
    """Importance weights; use arithmetic mean, never self-normalize the batch."""
    if not 0 < p < 1 or not 0 < q < 1:
        raise ValueError("Both class probabilities must be strictly between zero and one")
    return np.where(terminal, p / q, (1 - p) / (1 - q))


def subset(batch: SACBatch, indices: Any) -> SACBatch:
    source = SimpleNamespace(terminated=batch.source.terminated[indices])
    return SACBatch(
        source,  # type: ignore[arg-type]
        tree_map(lambda leaf: leaf[indices], batch.observations),
        batch.actions[indices],
        batch.rewards[indices],
        tree_map(lambda leaf: leaf[indices], batch.next_observations),
        batch.discounts[indices],
        None,
    )


def selected(model: Any, batch: SACBatch) -> tuple[torch.Tensor, torch.Tensor]:
    return tuple(
        critic(batch.observations).gather(1, batch.actions[:, None]).squeeze(1)
        for critic in (model.q1, model.q2)
    )


def materialize(replay: dict[str, Any], rows: np.ndarray, gamma: float) -> SACBatch:
    # Only shrink a disposable allocation when IDs have never wrapped. No replay
    # mutation/reset, persistence, sampler or runtime learner is involved.
    if replay["next_index"] != replay["size"]:
        raise ValueError("This probe requires a fresh, never-wrapped replay snapshot")
    store = InMemoryReplayStore(capacity=int(replay["size"]))
    store.load_state_dict({**replay, "capacity": int(replay["size"])})
    transitions, discounts = store.materialize_n_step(
        rows.tolist(), BatchRequest(batch_size=len(rows), n_step=1, gamma=gamma)
    )
    observations = tree_collate([item.observation for item in transitions])
    original = decode_tree(replay["observations"], rows)
    left: list[torch.Tensor] = []
    right: list[torch.Tensor] = []
    tree_map(lambda leaf: left.append(torch.as_tensor(leaf)), observations)
    tree_map(lambda leaf: right.append(torch.as_tensor(leaf)), original)
    assert len(left) == len(right)
    assert all(torch.equal(a, b) for a, b in zip(left, right, strict=True))
    for row, item, discount in zip(rows, transitions, discounts, strict=True):
        assert item.reward == replay["rewards"][row]
        assert item.terminated == replay["terminated"][row]
        assert item.truncated == replay["truncated"][row]
        assert item.step == replay["steps"][row]
        assert discount == (0 if item.terminated else gamma)
        assert torch.equal(
            torch.as_tensor(item.action), decode_tree(replay["actions"], np.array([row]))[0]
        )
    return discrete_batch(
        TrainingBatch(
            data=None,
            observations=observations,
            actions=torch.as_tensor(tree_collate([item.action for item in transitions])),
            rewards=torch.tensor([item.reward for item in transitions]),
            next_observations=tree_collate([item.next_observation for item in transitions]),
            terminated=torch.tensor([item.terminated for item in transitions]),
            truncated=torch.tensor([item.truncated for item in transitions]),
            bootstrap_discounts=torch.tensor(discounts),
            transition_ids=rows.tolist(),
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--original-checkpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    deadline = started + 600
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    assert not torch.cuda.is_available()
    hashes = {str(path): sha(path) for path in (args.checkpoint, args.original_checkpoint)}
    assert len(set(hashes.values())) == 1
    report: dict[str, Any] = {
        "started": datetime.now(UTC).isoformat(),
        "status": "RUNNING",
        "cap_seconds": 600,
        "copy_optimizer_steps": 0,
        "runtime_learner_updates": 0,
        "controller_created": False,
        "checkpoint_sha256": hashes,
        "script_sha256": sha(Path(__file__)),
        "results": [],
        "limitations": [
            "Held-out episodes were used by original training, excluded only from copy fitting.",
            "Frozen Bellman targets test regression and self-consistency, not critic truth.",
            "Nonterminal fitting uses a fixed random subset; empirical class mass is preserved.",
            "Sampling is with replacement; target critics, actor and alpha stay frozen.",
            "Terminal-only unweighted MSE changes the objective as a capacity control.",
            "No driving evaluation, new live training or saved policy change.",
        ],
    }

    def save() -> None:
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")

    save()
    state = read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    spec = RunSpec.from_yaml(args.config)
    fingerprint = run_fingerprint(spec, Path.cwd())
    assert spec.training.n_step == 1
    assert state["run_fingerprint"] == fingerprint
    report["fingerprint"] = fingerprint
    replay = state["replay_store"]
    terminal = np.asarray(replay["terminated"]) & ~np.asarray(replay["truncated"])
    codes = np.asarray(replay["episode_codes"])
    # Use complete terminal episodes only; do not fabricate an unfinished tail.
    complete = np.isin(codes, np.unique(codes[terminal]))
    eligible = np.flatnonzero(complete & ~np.asarray(replay["truncated"]))
    train, held = split_episodes(codes[eligible], seed=17421)
    train, held = eligible[train], eligible[held]
    rng = np.random.default_rng(17421)
    train_t, held_t = train[terminal[train]], held[terminal[held]]
    train_n = rng.choice(train[~terminal[train]], min(4096, (~terminal[train]).sum()), False)
    held_n = rng.choice(held[~terminal[held]], min(1024, (~terminal[held]).sum()), False)
    rows = np.r_[train_t, train_n, held_t, held_n]
    p = len(train_t) / len(train)
    report["split"] = {
        "seed": 17421,
        "train_episodes": np.unique(codes[train]).tolist(),
        "held_episodes": np.unique(codes[held]).tolist(),
        "train_eligible_rows": len(train),
        "empirical_terminal_probability": p,
        "selected_rows": rows.tolist(),
        "group_sizes": [len(train_t), len(train_n), len(held_t), len(held_n)],
    }
    print("Materializing saved transitions through frozen replay implementation", flush=True)
    batch = materialize(replay, rows, spec.training.gamma)
    assert not set(codes[train]) & set(codes[held])
    factory = spec.components.model_factory
    assert factory is not None
    model = _instantiate(factory).build()
    target = _instantiate(factory).build()
    model.load_state_dict(state["learner"]["model"], strict=True)
    target.load_state_dict(state["learner"]["target_model"], strict=True)
    model.eval().requires_grad_(False)
    target.eval().requires_grad_(False)
    digests = [model_digest(item) for item in (model, target)]
    context: Any = SimpleNamespace(model=model, target_model=target, q_clip_epsilon=0.5)
    context._desired_entropy = lambda count: 0.8
    alpha = max(float(state["learner"]["log_alpha"].exp()), 0.01)
    targets: list[torch.Tensor] = []
    anchors: list[torch.Tensor] = []
    audit_q: list[torch.Tensor] = []
    for offset in range(0, len(rows), 128):
        chunk = subset(batch, slice(offset, offset + 128))
        targets.append(
            StableDiscreteSoftActorCritic._critic_targets(context, chunk, torch.tensor(alpha))
        )
        with torch.no_grad():
            anchors.append(torch.stack(selected(target, chunk)))
            audit_q.append(torch.stack(selected(model, chunk)))
    fixed_targets, fixed_anchors, initial_q = (
        torch.cat(targets),
        torch.cat(anchors, 1),
        torch.cat(audit_q, 1),
    )
    terminal_mask = batch.source.terminated
    assert torch.equal(fixed_targets[terminal_mask], batch.rewards[terminal_mask])
    gradients = initial_q.clone().requires_grad_()
    losses, diagnostics = StableDiscreteSoftActorCritic._critic_losses(
        context,
        subset(batch, torch.where(terminal_mask)[0]),
        (gradients[0, terminal_mask], gradients[1, terminal_mask], fixed_targets[terminal_mask]),
    )
    grad = torch.autograd.grad(losses.sum(), gradients)[0][:, terminal_mask]
    error = initial_q[:, terminal_mask] - fixed_targets[terminal_mask]
    report["alignment_gradient_audit"] = {
        "materialized_rows_checked": len(rows),
        "terminal_targets_exact_reward": True,
        "terminal_count": int(terminal_mask.sum()),
        "terminal_zero_gradient_fraction": float((grad == 0).float().mean()),
        "terminal_wrong_direction_fraction": float((grad * error < 0).float().mean()),
        "terminal_clip_blocked_fraction": float(
            diagnostics["critic/clip_blocked_gradient_fraction"]
        ),
        "nonblocked_gradient_matches_mse": bool(
            torch.allclose(grad[grad != 0], (2 * error)[grad != 0])
        ),
    }
    boundaries = np.cumsum([0, len(train_t), len(train_n), len(held_t), len(held_n)])
    group_names = ("train_terminal", "train_nonterminal", "held_terminal", "held_nonterminal")

    def evaluate(item: Any) -> dict[str, Any]:
        chunks = []
        with torch.no_grad():
            for offset in range(0, len(rows), 128):
                chunks.append(
                    torch.stack(selected(item, subset(batch, slice(offset, offset + 128))))
                )
        q = torch.cat(chunks, 1)
        return {
            name: {
                "count": int(end - begin),
                "mae": float((q[:, begin:end] - fixed_targets[begin:end]).abs().mean()),
                "bias": float((q[:, begin:end] - fixed_targets[begin:end]).mean()),
                "q_drift": float((q[:, begin:end] - initial_q[:, begin:end]).abs().mean()),
            }
            for name, begin, end in zip(group_names, boundaries[:-1], boundaries[1:], strict=True)
        }

    report["baseline"] = evaluate(model)
    report["alpha"] = alpha
    save()
    for mode in ("empirical_uniform", "stratified_corrected", "terminal_only_capacity"):
        for seed in (17, 29):
            candidate = copy.deepcopy(model)
            candidate.q1.requires_grad_(True)
            candidate.q2.requires_grad_(True)
            optimizer = torch.optim.Adam(
                list(candidate.q1.parameters()) + list(candidate.q2.parameters()), lr=0.0003
            )
            optimizer.load_state_dict(copy.deepcopy(state["learner"]["critic_optimizer"]))
            random = np.random.default_rng(seed)
            result: dict[str, Any] = {"mode": mode, "seed": seed, "steps": 0, "terminal_draws": 0}
            report["results"].append(result)
            print(f"Copy optimization: {mode}, seed {seed}", flush=True)
            for step in range(64):
                if time.monotonic() >= deadline:
                    report["status"] = "CAPPED_PARTIAL"
                    break
                q = p if mode == "empirical_uniform" else 0.125
                mask = random.random(128) < q
                if mode == "terminal_only_capacity":
                    mask[:] = True
                indices = np.where(
                    mask,
                    random.integers(0, len(train_t), 128),
                    random.integers(len(train_t), len(train_t) + len(train_n), 128),
                )
                current = torch.stack(selected(candidate, subset(batch, indices)))
                raw = (current - fixed_targets[indices]).square()
                if mode == "terminal_only_capacity":
                    loss = raw.sum(0).mean()
                else:
                    clipped = fixed_anchors[:, indices] + (
                        current - fixed_anchors[:, indices]
                    ).clamp(-0.5, 0.5)
                    losses = torch.maximum(raw, (clipped - fixed_targets[indices]).square()).sum(0)
                    weights = torch.tensor(class_weights(mask, p, q), dtype=losses.dtype)
                    loss = (weights * losses).mean()
                assert bool(torch.isfinite(loss))
                optimizer.zero_grad(set_to_none=True)
                loss.backward()  # type: ignore[no-untyped-call]
                optimizer.step()
                result["steps"] = step + 1
                result["terminal_draws"] += int(mask.sum())
                report["copy_optimizer_steps"] += 1
            result["metrics"] = evaluate(candidate)
            result["actor_unchanged"] = model_digest(candidate.actor) == model_digest(model.actor)
            assert result["actor_unchanged"]
            save()
            del optimizer, candidate
    assert digests == [model_digest(item) for item in (model, target)]
    assert hashes == {path: sha(Path(path)) for path in hashes}
    report["immutable_checkpoints_and_base_models_unchanged"] = True
    report["optimizer_state"] = "Independent deep copies of saved critic Adam state"
    report["elapsed_seconds"] = time.monotonic() - started
    report["finished"] = datetime.now(UTC).isoformat()
    if report["status"] == "RUNNING":
        report["status"] = "COMPLETE"
    save()
    print(
        f"{report['status']}: {report['copy_optimizer_steps']} disposable optimizer steps",
        flush=True,
    )


if __name__ == "__main__":
    main()
