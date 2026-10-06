"""Compare selected-action Q with recorded returns; never trains or controls a game.

Replay was collected by older policies. Its soft return is a behavior-policy proxy,
not an unbiased target for the current policy and not a ranking of unchosen actions.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RecordedValue:
    step: int
    reward: float
    behavior_entropy: float
    q1: float
    q2: float
    terminated: bool
    truncated: bool = False
    stratum: str = "all"


def _summary(rows: Sequence[tuple[float, float, float]]) -> dict[str, float | int]:
    errors = [q - soft for q, soft, _ in rows]
    size = len(rows)
    return {
        "states": size,
        "q_mean": sum(q for q, _, _ in rows) / size,
        "behavior_soft_return_mean": sum(soft for _, soft, _ in rows) / size,
        "reward_return_mean": sum(raw for _, _, raw in rows) / size,
        "soft_return_bias": sum(errors) / size,
        "soft_return_rmse": math.sqrt(sum(e * e for e in errors) / size),
        "soft_return_mae": sum(abs(e) for e in errors) / size,
    }


def recorded_return_report(
    episodes: Mapping[str, Sequence[RecordedValue]], *, gamma: float, alpha: float
) -> dict[str, Any]:
    """Use complete contiguous terminated episodes, excluding truncated/missing tails.

    Q(s_t,a_t) includes reward_t and future entropy, not entropy at s_t. No
    bootstrap is invented for episodes whose continuation was not recorded.
    """
    if not math.isfinite(gamma) or not 0 <= gamma <= 1:
        raise ValueError("gamma must be finite and in [0, 1]")
    if not math.isfinite(alpha) or alpha <= 0:
        raise ValueError("alpha must be finite and positive")
    groups: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    accepted, excluded = [], []
    for episode_id, rows in episodes.items():
        for row in rows:
            if (
                not all(
                    math.isfinite(value)
                    for value in (row.reward, row.behavior_entropy, row.q1, row.q2)
                )
                or row.behavior_entropy < 0
            ):
                raise ValueError(f"Invalid recorded values in episode {episode_id}")
        complete = bool(rows) and rows[-1].terminated and not rows[-1].truncated
        contiguous = all(row.step == i for i, row in enumerate(rows))
        early_end = any(row.terminated or row.truncated for row in rows[:-1])
        if not complete or not contiguous or early_end:
            excluded.append(episode_id)
            continue
        accepted.append(episode_id)
        raw_return, soft_return, next_entropy = 0.0, 0.0, 0.0
        for row in reversed(rows):
            raw_return = row.reward + gamma * raw_return
            soft_return = row.reward + gamma * (soft_return + alpha * next_entropy)
            next_entropy = row.behavior_entropy
            entry = (0.5 * (row.q1 + row.q2), soft_return, raw_return)
            groups["all"].append(entry)
            if row.stratum not in {"all", "episode_start", "terminal"}:
                groups[row.stratum].append(entry)
            if row.step == 0:
                groups["episode_start"].append(entry)
            if row.terminated:
                groups["terminal"].append(entry)
    return {
        "comparison_target": "recorded_behavior_soft_return_proxy",
        "gamma": gamma,
        "alpha": alpha,
        "complete_episodes": len(accepted),
        "excluded_episodes": excluded,
        "groups": {name: _summary(rows) for name, rows in groups.items()},
        "limitations": [
            "Historical behavior differs from the current policy; no on-policy calibration claim.",
            "No counterfactual ranking of unchosen actions can be inferred.",
            "Incomplete or truncated episodes have no invented bootstrap.",
        ],
        "driving_gate_passed": False,
    }
