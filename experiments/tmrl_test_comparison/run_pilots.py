"""Run pilots sequentially, stopping on errors or stop request."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    directory = Path(sys.argv[1]).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    stop = directory / "STOP"
    algorithms = sys.argv[2:] or ("iqn", "qr", "sd-sac", "tqc", "ppo")
    for algorithm in algorithms:
        algorithm = {"discrete-sac": "sd-sac", "dsac": "sd-sac"}.get(algorithm, algorithm)
        if stop.exists():
            break
        config = ROOT / "experiments/tmrl_test_comparison/configs/pilot" / f"{algorithm}-s17.yaml"
        state = {"algorithm": algorithm, "started": datetime.now(timezone.utc).isoformat(), "status": "running"}
        (directory / "status.json").write_text(json.dumps(state, indent=2))
        with (directory / f"{algorithm}.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(
                [sys.executable, "-u", "-m", "trackmaniarl", "train", str(config), "--stop-file", str(stop)],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
            )
        state.update(returncode=result.returncode, status="stopped" if stop.exists() else "completed" if result.returncode == 0 else "failed", ended=datetime.now(timezone.utc).isoformat())
        (directory / "status.json").write_text(json.dumps(state, indent=2))
        with (directory / "history.jsonl").open("a", encoding="utf-8") as history:
            history.write(json.dumps(state) + "\n")
        if result.returncode or stop.exists():
            break


if __name__ == "__main__":
    main()
