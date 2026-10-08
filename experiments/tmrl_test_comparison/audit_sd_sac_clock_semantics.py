"""Check absolute-clock visibility in the frozen feature pipeline; no learning or controller."""

from __future__ import annotations

import argparse
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

from trackmaniarl.core.runtime import _instantiate
from trackmaniarl.core.spec import RunSpec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    spec = RunSpec.from_yaml(args.config)
    low, high = (_instantiate(spec.components.feature_pipeline) for _ in range(2))
    values: Any = np.zeros(33, dtype=np.float32)
    values[4:7] = low._reward_center[0]
    tangent = low._tangent_xz(0)
    values[[10, 12]] = tangent
    values[[7, 9]] = 10 * tangent
    values[16] = 10
    values[29] = 1
    frames = []
    for clock in (0.0, 50.0):
        earlier = values.copy()
        later = values.copy()
        earlier[3], later[3] = clock, clock + 149900
        a, b = low.transform_observation(earlier), high.transform_observation(later)
        errors = {k: float((a[k] - b[k]).abs().max()) for k in a}
        assert all(torch.equal(a[k], b[k]) for k in a)
        frames.append(
            {"race_time_ms": [float(earlier[3]), float(later[3])], "max_branch_error": errors}
        )
    cfg = spec.components.environment.kwargs["config"]
    report = {
        "status": "COMPLETE",
        "optimizer_steps": 0,
        "controller_created": False,
        "cpu_threads": 1,
        "priority": "IDLE",
        "frames": frames,
        "maximum_race_time_s": cfg["maximum_race_time_s"],
        "finding": (
            "The actual V5 transform maps these clock-shifted equal-motion histories "
            "to identical prepared observations."
        ),
        "semantics": (
            "The configured race deadline is a penalized terminal; "
            "collection interruptions are truncations."
        ),
        "limitations": [
            "Synthetic representation control, not an alias found in saved replay.",
            "No proof that clock omission causes failed starts or driving failure.",
            "Changing terminal to truncated would change the tested task objective.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
