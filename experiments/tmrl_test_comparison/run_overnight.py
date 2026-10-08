"""Run an explicit pilot schedule with graceful per-run deadlines and a global STOP."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import psutil

from experiments.tmrl_test_comparison.policy import require_standard_config
from trackmaniarl.observability.wandb_metrics import _load_wandb_key_from_dotenv

ROOT = Path(__file__).resolve().parents[2]


def write_status(directory: Path, state: dict) -> None:
    temporary = directory / "status.tmp"
    temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temporary.replace(directory / "status.json")


def run_one(directory: Path, entry: dict, seconds: float) -> dict:
    require_standard_config(Path(entry["config"]))
    name = entry["name"]
    stop = directory / f"STOP-{name}"
    if stop.exists():
        raise RuntimeError(f"Refusing to reuse a stopped attempt: {stop}")
    state = {
        "name": name,
        "config": entry["config"],
        "run_id": entry["run_id"],
        "started": datetime.now(UTC).isoformat(),
        "status": "running",
    }
    started = time.monotonic()
    stop_at = None
    children: dict[int, psutil.Process] = {}
    with (directory / f"{name}.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-u",
                "-m",
                "trackmaniarl",
                "train",
                entry["config"],
                "--stop-file",
                str(stop),
            ],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        parent = psutil.Process(process.pid)
        state["pid"] = process.pid
        while process.poll() is None:
            try:
                for child in parent.children(recursive=True):
                    children[child.pid] = child
            except psutil.NoSuchProcess:
                pass
            elapsed = time.monotonic() - started
            if stop_at is None and ((directory / "STOP").exists() or elapsed >= seconds):
                stop.touch()
                stop_at = time.monotonic()
                state["status"] = "saving"
                state["stop_reason"] = "user" if (directory / "STOP").exists() else "time_limit"
            state["elapsed_s"] = round(elapsed, 1)
            write_status(directory, state)
            if stop_at is not None and time.monotonic() - stop_at > 600:
                state["status"] = "shutdown_timeout"
                write_status(directory, state)
                # Do not overlap the next pilot with a still-running game controller.
                raise RuntimeError("Training did not shut down within ten minutes; queue stopped.")
            time.sleep(2)
        state["returncode"] = process.returncode
    # Never start the next controller until descendants of this attempt have exited.
    _, alive = psutil.wait_procs(list(children.values()), timeout=30)
    if alive:
        state["status"] = "orphaned_children"
        state["remaining_pids"] = [p.pid for p in alive]
        write_status(directory, state)
        raise RuntimeError("Descendants are still running; queue stopped.")
    state["status"] = (
        "failed"
        if process.returncode
        else "time_limited"
        if state.get("stop_reason") == "time_limit"
        else "stopped"
        if state.get("stop_reason") == "user"
        else "completed"
    )
    state["elapsed_s"] = round(time.monotonic() - started, 1)
    state["ended"] = datetime.now(UTC).isoformat()
    write_status(directory, state)
    with (directory / "history.jsonl").open("a", encoding="utf-8") as history:
        history.write(json.dumps(state) + "\n")
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--key-source-root", type=Path, required=True)
    parser.add_argument("--hours", type=float, default=2.25)
    args = parser.parse_args()
    if not 0 < args.hours <= 3:
        raise ValueError("Pilot duration must be in (0, 3] hours")
    directory = args.directory.resolve()
    schedule = json.loads((directory / "schedule.json").read_text(encoding="utf-8"))
    for entry in schedule:
        require_standard_config(Path(entry["config"]))
    _load_wandb_key_from_dotenv(str(args.key_source_root.resolve()))
    if not os.environ.get("WANDB_API_KEY"):
        raise RuntimeError("W&B API key is unavailable; refusing an untracked pilot.")
    os.environ["WANDB_MODE"] = "online"
    os.environ.setdefault("WANDB_ENTITY", "dsc-pjatk-warsaw")
    # An interrupted schedule is resumed deliberately using a new directory.
    if (directory / "history.jsonl").exists():
        raise RuntimeError("Schedule already has history; refusing duplicate training.")
    for entry in schedule:
        if (directory / "STOP").exists():
            break
        result = run_one(directory, entry, args.hours * 3600)
        print(json.dumps(result), flush=True)
        if result["status"] in {"failed", "stopped"}:
            break
    else:
        write_status(
            directory, {"status": "queue_completed", "ended": datetime.now(UTC).isoformat()}
        )


if __name__ == "__main__":
    main()
