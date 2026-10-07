"""Materialize and launch one fresh, human-authorized bounded actor-fit pilot."""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import psutil
import yaml

BASE = Path("H:/Studia/inzynierskie/inzynierkav2/AITrackmania/artifacts/tmrl-test-comparison")
ROOT = BASE / "sd-fit07d"
OLD = BASE / "sd-af07"
EDITABLE = Path("C:/Users/szulc/.codex/worktrees/tmrl-training-fixes/AITrackmania")
RUNTIME = Path("C:/Users/szulc/.codex/worktrees/tmrl-sd-sac-actorfit-runtime/AITrackmania")
COMMIT = "281332d99fdb8bc1edb70d590260731699ab40bf"
AUTHORIZATION = "gra odpalona to odpalaj test by w ko\u0144cu sd sac dzia\u0142a\u0142"


def read(path: Path | str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(Path(path).read_text(encoding="utf-8")))


def sha(path: Path | str) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def modules() -> tuple[ModuleType, ModuleType]:
    sys.path.insert(0, str(ROOT))
    import runner
    import sd_sac_runner

    return runner, sd_sac_runner


def predecessor(core: ModuleType, reviewed: ModuleType) -> dict[str, Any]:
    failed = BASE / "sd-fit07"
    closure = read(failed / "post-closure-verification.json")
    if not all(
        closure.get(k) is True for k in ("all_owned_closed", "mutex_free", "immutable_pins_valid")
    ):
        raise RuntimeError("Failed preflight attempt must be fully closed")
    if any(reviewed.alive(p) for p in closure["owned_processes"]):
        raise RuntimeError("Failed preflight child still active")
    reviewed.check_frozen_files(failed)
    if core.global_stop(failed, read(failed / "plan.json")):
        raise RuntimeError("New STOP in failed preflight queue wins")
    previous = read(OLD / "human-stop-verification.json")
    if not all(
        previous.get(k) is True for k in ("all_owned_closed", "mutex_free", "immutable_pins_valid")
    ):
        raise RuntimeError("Missing predecessor closure evidence")
    if previous["normal_closure"]["forced_owned_pids"] != []:
        raise RuntimeError("Forced predecessor closure")
    if any(reviewed.alive(p) for p in previous["owned_processes"]):
        raise RuntimeError("Previous owned process remains active")
    reviewed.check_frozen_files(OLD)
    cp = previous["checkpoint"]
    if sha(cp["checkpoint"]) != cp["checkpoint_sha256"]:
        raise RuntimeError("Stopped checkpoint changed")
    if sha(OLD / "STOP") != previous["STOP_sha256"]:
        raise RuntimeError("New or changed human STOP")
    core.assert_no_controller()
    return previous


def prepare() -> None:
    from experiments.tmrl_test_comparison.prepare_sd_sac_actorfit import (
        _resolved_config,
        validate_scope,
    )

    if ROOT.exists():
        raise RuntimeError("Never reuse a prepared or launched queue")
    ROOT.mkdir()
    for name in (
        "runner.py",
        "runtime_helper.py",
        "owned_processes.py",
        "sd_sac_runner.py",
        "sd_sac_deadline_guard.py",
        "test_sd_sac_guards.py",
    ):
        shutil.copyfile(OLD / name, ROOT / name)
    shutil.copyfile(__file__, ROOT / "pilot.py")
    core, reviewed = modules()
    previous = predecessor(core, reviewed)
    with core.ControllerLease():
        pass
    old_plan = read(OLD / "plan.json")
    exemptions = copy.deepcopy(old_plan["superseded_stops"])
    # This new direct human start supersedes only these exact previous STOP files.
    for path in (OLD / "STOP", OLD / "STOP-sd-sac"):
        exemptions.append(
            {"path": str(path), "sha256": sha(path), "mtime_ns": path.stat().st_mtime_ns}
        )
    exempt_paths = {Path(p["path"]).resolve() for p in exemptions}
    stops = {Path(p).resolve() for p in old_plan["stop_sources"]} - exempt_paths
    stops.update((ROOT / p).resolve() for p in ("STOP", "STOP-sd-sac", "STOP-eval-sd-sac"))
    for previous_attempt in ("sd-fit07", "sd-fit07b", "sd-fit07c"):
        stops.update(
            (BASE / previous_attempt / p).resolve()
            for p in ("STOP", "STOP-sd-sac", "STOP-eval-sd-sac")
        )
    stops.update(
        (RUNTIME / p).resolve() for p in ("STOP", "artifacts/STOP", "artifacts/STOP-sd-sac")
    )
    candidate_path = (
        EDITABLE / "experiments/tmrl_test_comparison/configs/diagnostic/sd-sac-actorfit-s17.yaml"
    )
    candidate = _resolved_config(candidate_path)
    candidate["artifacts_dir"] = str(BASE)
    validate_scope(_resolved_config(OLD / "sd-sac.yaml"), candidate)
    (ROOT / "sd-sac.yaml").write_text(yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8")
    train = {
        "name": "sd-sac",
        "kind": "train",
        "runtime": str(RUNTIME),
        "source_commit": COMMIT,
        "config": str(ROOT / "sd-sac.yaml"),
        "run_id": candidate["run_id"],
        "max_seconds": 11400,
        "target_transitions": 145408,
    }
    evaluation = {
        "name": "eval-sd-sac",
        "kind": "benchmark",
        "runtime": str(RUNTIME),
        "source_commit": COMMIT,
        "config": str(ROOT / "eval.yaml"),
        "run_id": candidate["run_id"] + "-eval10",
        "max_seconds": 2100,
        "trials": 10,
        "config_from_train": "sd-sac",
        "checkpoint_from_train": "sd-sac",
    }
    plan = {
        "schema_version": 1,
        "maximum_seconds": 14400,
        "entries": [train, evaluation],
        "authorization": AUTHORIZATION,
        "fresh_start": True,
        "automatic_full_training": False,
        "predecessor": str(OLD),
        "original_checkpoint": previous["checkpoint"]["checkpoint"],
        "stop_sources": [str(p) for p in sorted(stops)],
        "superseded_stops": exemptions,
        "hypothesis": "Objective-only SAC to experimental forward KL; "
        "critic truth and driving remain unproven.",
    }
    core.atomic_json(ROOT / "plan.json", plan)
    core.atomic_json(
        ROOT / "RESUME-AUTHORIZATION.json",
        {
            "human_instruction": AUTHORIZATION,
            "scope": "One fresh 145408-transition pilot plus ten greedy trials; "
            "no checkpoint resume or full training",
            "historical_stop_exceptions": exemptions,
            "new_or_changed_STOP_wins": True,
        },
    )
    pins = copy.deepcopy(read(OLD / "source-freeze.json")["helpers"])
    # Every tracked runtime source is immutable, including added diagnostics and preparation tools.
    files = subprocess.check_output(
        ["git", "-C", str(RUNTIME), "ls-files", "trackmaniarl", "experiments"], text=True
    ).splitlines()
    for rel in files:
        p = RUNTIME / rel
        if p.is_file():
            pins[str(p)] = sha(p)
    env = candidate["components"]["environment"]["kwargs"]["config"]
    assets = [
        env["geometry_path"],
        env["steering_curve_path"],
        candidate["components"]["feature_pipeline"]["kwargs"]["geometry_path"],
    ]
    for item in candidate["evaluation"]["maps"]:
        assets.extend([item["map_path"], item["geometry_path"]])
    for p in [
        *assets,
        previous["checkpoint"]["checkpoint"],
        OLD / "human-stop-verification.json",
        BASE / "sd-fit07/post-closure-verification.json",
        BASE / "sd-fit07/source-freeze.json",
        BASE / "sd-af07-actor-fit-20261007/comparison.json",
        *ROOT.iterdir(),
    ]:
        if Path(p).is_file():
            pins[str(p)] = sha(p)
    commit = subprocess.check_output(
        ["git", "-C", str(RUNTIME), "rev-parse", "HEAD"], text=True
    ).strip()
    core.atomic_json(
        ROOT / "source-freeze.json",
        {"runtime": str(RUNTIME), "source_commit": commit, "helpers": pins},
    )
    validate()
    print(
        "PREPARED_NOT_LAUNCHED: fresh objective-only pilot; "
        "predecessor/STOP/source/asset/SHA and bounds checked"
    )


def validate() -> tuple[dict[str, Any], dict[str, Any]]:
    from experiments.tmrl_test_comparison.prepare_sd_sac_actorfit import (
        _resolved_config,
        validate_scope,
    )

    core, reviewed = modules()
    plan = read(ROOT / "plan.json")
    if (
        plan["maximum_seconds"] != 14400
        or plan["automatic_full_training"] is not False
        or not plan["fresh_start"]
    ):
        raise RuntimeError("Bounded fresh scope changed")
    train, evaluation = plan["entries"]
    if (
        train["kind"],
        train["target_transitions"],
        train["max_seconds"],
        evaluation["trials"],
        evaluation["max_seconds"],
    ) != ("train", 145408, 11400, 10, 2100):
        raise RuntimeError("Stage bounds changed")
    for entry in plan["entries"]:
        if (
            entry["runtime"] != str(RUNTIME)
            or entry["source_commit"] != COMMIT
            or entry.get("checkpoint")
        ):
            raise RuntimeError("Pinned fresh runtime required")
    candidate = _resolved_config(Path(train["config"]))
    validate_scope(_resolved_config(OLD / "sd-sac.yaml"), candidate)
    configs = {"sd-sac": candidate, "eval-sd-sac": core.diagnostic_config(candidate, evaluation)}
    for entry in plan["entries"]:
        core.validate_config(configs[entry["name"]], entry)
    if (BASE / train["run_id"]).exists():
        raise RuntimeError("Training identity already used")
    reviewed.check_frozen_files(ROOT)
    if core.global_stop(ROOT, plan):
        raise RuntimeError("New or changed STOP wins")
    predecessor(core, reviewed)
    return plan, configs


def launch() -> None:
    core, reviewed = modules()
    plan, configs = validate()
    if any((ROOT / p).exists() for p in ("launch.json", "history.jsonl")):
        raise RuntimeError("Used queue cannot restart")
    done = threading.Event()
    observed = {}

    def observe() -> None:
        while not done.wait(0.2):
            for process in [psutil.Process(), *psutil.Process().children(recursive=True)]:
                with contextlib.suppress(psutil.NoSuchProcess):
                    observed[(process.pid, process.create_time())] = {
                        "pid": process.pid,
                        "created_time": process.create_time(),
                    }
            core.atomic_json(
                ROOT / "live-owned-identity-receipt.json",
                {"owned_processes": list(observed.values())},
            )

    with core.ControllerLease():
        core.assert_no_controller()
        core.load_tracking_key(BASE.parents[1])
        budget = core.Budget(seconds=14400, save_margin=600)
        receipt = dict(
            **budget.manifest(),
            pid=os.getpid(),
            created_time=psutil.Process().create_time(),
            entries=plan["entries"],
            plan_sha256=sha(ROOT / "plan.json"),
            fresh_start=True,
            automatic_full_training=False,
        )
        core.atomic_json(ROOT / "launch.json", receipt)
        with (ROOT / "guard.log").open("x", encoding="utf-8") as log:
            guard = subprocess.Popen(
                [sys.executable, "-u", str(ROOT / "sd_sac_deadline_guard.py"), str(ROOT)],
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        core.atomic_json(
            ROOT / "guard-start.json",
            {"pid": guard.pid, "created_time": psutil.Process(guard.pid).create_time()},
        )
        core.atomic_json(ROOT / "actual-launch-receipt.json", receipt)
        core.atomic_json(BASE / "active-queue.json", dict(queue=str(ROOT), **receipt))
        watcher = threading.Thread(target=observe, daemon=True)
        watcher.start()
        try:
            core.execute_plan(ROOT, plan, configs, budget)
            if read(ROOT / "status.json")["status"] == "queue_completed":
                completion = read(ROOT / "sd-sac-completion.json")
                evaluation = read(ROOT / "eval-sd-sac-evaluation.json")
                core.atomic_json(
                    ROOT / "sd-sac-repair-decision.json",
                    reviewed.assess_repair(completion, read(evaluation["artifact"])),
                )
        except BaseException as exc:
            core.write_status(
                ROOT,
                {
                    "status": "queue_failed",
                    "exception": type(exc).__name__,
                    "message": str(exc),
                    "at": core.utc_now().isoformat(),
                },
            )
            raise
        finally:
            done.set()
            watcher.join(timeout=5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.validate_only:
        validate()
        print("VALID: no controller created")
    else:
        launch()
