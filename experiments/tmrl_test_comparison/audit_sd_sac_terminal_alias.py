"""Inspect exact decoded terminal aliases and sampled observation neighbors; zero updates."""

from __future__ import annotations

import argparse
import hashlib
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
from trackmaniarl.core.spec import RunSpec


def leaves(tree: Any, prefix: str = "") -> dict[str, torch.Tensor]:
    if isinstance(tree, dict):
        return {
            p: v for k in sorted(tree) for p, v in leaves(tree[k], prefix + "/" + str(k)).items()
        }
    if isinstance(tree, (tuple, list)):
        return {
            p: v for k, x in enumerate(tree) for p, v in leaves(x, prefix + "/" + str(k)).items()
        }
    return {prefix: tree}


def hashes(flat: dict[str, torch.Tensor]) -> list[str]:
    result = []
    for row in range(len(next(iter(flat.values())))):
        digest = hashlib.sha256()
        for path, tensor in flat.items():
            digest.update(path.encode())
            digest.update(str(tensor.shape[1:]).encode())
            digest.update(str(tensor.dtype).encode())
            digest.update(tensor[row].contiguous().numpy().tobytes())
        result.append(digest.hexdigest())
    return result


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
    support = importlib.util.spec_from_file_location(
        "alias_support", Path(__file__).with_name("probe_sd_sac_actor_plasticity.py")
    )
    assert support is not None
    assert support.loader is not None
    h = importlib.util.module_from_spec(support)
    support.loader.exec_module(h)
    helper = h.load_helper()
    assert helper.sha(args.checkpoint) == args.expected_sha
    state = helper.read_checkpoint(args.checkpoint, temporary_directory=args.output.parent)
    assert run_fingerprint(RunSpec.from_yaml(args.config), Path.cwd()) == state["run_fingerprint"]
    pin = helper.tree_digest(state["learner"])
    replay = state["replay_store"]
    size = int(replay["size"])
    terminated = np.asarray(replay["terminated"][:size], dtype=bool)
    terminals = np.flatnonzero(terminated)
    nonterminals = np.flatnonzero(~terminated)
    actions = helper.decode_tree(replay["actions"], np.arange(size)).numpy().reshape(-1)
    episodes = np.asarray(replay["episode_codes"][:size])
    steps = np.asarray(replay["steps"][:size])
    begun = time.monotonic()

    def cap() -> None:
        if time.monotonic() - begun > 180:
            raise TimeoutError("Fixed 180s audit cap")

    terminal_hashes = hashes(leaves(helper.decode_tree(replay["observations"], terminals)))
    lookup: dict[str, list[int]] = {}
    for row, digest in zip(terminals, terminal_hashes, strict=True):
        lookup.setdefault(digest, []).append(int(row))
    aliases: list[tuple[int, int]] = []
    for offset in range(0, size, 256):
        cap()
        selected = np.arange(offset, min(offset + 256, size))
        decoded_hashes = hashes(leaves(helper.decode_tree(replay["observations"], selected)))
        for row, digest in zip(selected, decoded_hashes, strict=True):
            if not terminated[row] and digest in lookup:
                aliases.extend((t, int(row)) for t in lookup[digest])

    rng = np.random.default_rng(17421)
    sample = rng.choice(nonterminals, min(4096, len(nonterminals)), replace=False)
    # Add immediate predecessors explicitly; nearest-neighbor coverage remains sampled.
    predecessor = [
        int(r)
        for r in nonterminals
        if any((episodes[r] == episodes[t]) and (steps[r] + 1 == steps[t]) for t in terminals)
    ]
    sample = np.unique(np.concatenate((sample, predecessor))).astype(np.int64)
    terminal_obs = leaves(helper.decode_tree(replay["observations"], terminals))
    sample_obs = leaves(helper.decode_tree(replay["observations"], sample))
    distances: Any = np.zeros((len(terminals), len(sample)), dtype=np.float64)
    branch_distances = {}
    branch_scales = {}
    for path in terminal_obs:
        cap()
        a = terminal_obs[path].double().reshape(len(terminals), -1)
        b = sample_obs[path].double().reshape(len(sample), -1)
        # One scale per branch; equal branch weight prevents large graph arrays dominating.
        scale = float((b - b.mean(0)).square().mean().sqrt())
        scale = max(scale, 1e-6)
        d = (
            (a.square().mean(1)[:, None] + b.square().mean(1)[None, :] - 2 * a @ b.T / a.shape[1])
            .clamp_min(0)
            .numpy()
        )
        branch_distances[path] = np.sqrt(d)
        branch_scales[path] = scale
        distances += d / scale**2
    distances = np.sqrt(distances / len(terminal_obs))

    def metadata(row: int) -> dict[str, Any]:
        return {
            "row": row,
            "episode": int(episodes[row]),
            "step": int(steps[row]),
            "action": int(actions[row]),
            "reward": float(replay["rewards"][row]),
            "terminated": bool(terminated[row]),
            "truncated": bool(replay["truncated"][row]),
        }

    neighbors = []
    for i, row in enumerate(terminals):
        groups: dict[str, Any] = {}
        for name, mask in {
            "any": np.ones(len(sample), dtype=bool),
            "different_episode": episodes[sample] != episodes[row],
            "same_action_different_episode": (episodes[sample] != episodes[row])
            & (actions[sample] == actions[row]),
        }.items():
            candidates = np.flatnonzero(mask)
            if not len(candidates):
                groups[name] = None
                continue
            j = int(candidates[np.argmin(distances[i, candidates])])
            groups[name] = {
                "neighbor": metadata(int(sample[j])),
                "distance": float(distances[i, j]),
                "raw_branch_rms": {p: float(d[i, j]) for p, d in branch_distances.items()},
            }
        neighbors.append({"terminal": metadata(int(row)), "groups": groups})
    cap()
    assert helper.tree_digest(state["learner"]) == pin
    assert helper.sha(args.checkpoint) == args.expected_sha
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
        "replay_rows": size,
        "terminal_rows": len(terminals),
        "nonterminal_rows": len(nonterminals),
        "exact_hash_scope": "All saved current observations; path/shape/dtype/decoded bytes",
        "exact_terminal_nonterminal_pairs": [
            {
                "terminal": metadata(t),
                "nonterminal": metadata(n),
                "same_action": bool(actions[t] == actions[n]),
            }
            for t, n in aliases
        ],
        "neighbor_sample_rows": sample.tolist(),
        "branch_scales": branch_scales,
        "neighbors": neighbors,
        "limitations": [
            "Neighbors use a fixed sample plus predecessors; distances are not exhaustive.",
            "Branch-scaled RMS is descriptive and is not a learned separability classifier.",
            "Current observations precede actions; outcomes may depend on hidden history.",
            "An observation/action alias alone does not establish an incorrect label.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {k: report[k] for k in ("status", "elapsed_seconds", "replay_rows", "terminal_rows")}
        )
    )


if __name__ == "__main__":
    main()
