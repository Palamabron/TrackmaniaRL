"""Exercise an installed release from outside the checkout, including a starter.

Run only in a disposable environment: this installs the generated extension.
Requires uv on PATH but no game, GPU or optional runtime integrations.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def _run(arguments: list[str], cwd: Path) -> str:
    result = subprocess.run(arguments, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        # Captured output can contain local account paths or configuration values.
        raise RuntimeError(f"Installed release smoke command failed with exit {result.returncode}")
    return result.stdout


def main() -> None:
    import trackmaniarl

    checkout = Path(__file__).resolve().parents[1]
    installed = Path(trackmaniarl.__file__).resolve()
    if installed.is_relative_to(checkout / "trackmaniarl"):
        raise RuntimeError("Smoke test requires an installed wheel, not the source checkout")
    assert trackmaniarl.__version__ == importlib.metadata.version("TrackmaniaRL")
    for namespace in (
        "core",
        "algorithms",
        "models",
        "trackmania",
        "experiments",
        "observability",
        "distributed",
    ):
        importlib.import_module(f"trackmaniarl.{namespace}")
    with tempfile.TemporaryDirectory(prefix="trackmaniarl-release-") as temporary:
        work = Path(temporary)
        cli = [sys.executable, "-m", "trackmaniarl"]
        _run([*cli, "--help"], work)
        _run([*cli, "--version"], work)
        _run([*cli, "init", "starter", "--template", "starter"], work)
        _run([*cli, "init", "game", "--template", "trackmania"], work)
        starter = work / "starter"
        _run(
            [
                "uv",
                "--no-config",
                "pip",
                "install",
                "--no-deps",
                "--python",
                sys.executable,
                str(starter),
            ],
            work,
        )
        _run([*cli, "inspect-config", "run.yaml"], starter)
        _run([*cli, "validate", "run.yaml"], starter)
        invalid = subprocess.run(
            [*cli, "unknown-command"],
            cwd=work,
            capture_output=True,
            text=True,
        )
        assert invalid.returncode == 2
        print(
            json.dumps(
                {
                    "version": trackmaniarl.__version__,
                    "installed_import": True,
                    "help": True,
                    "templates": 2,
                    "inspect": True,
                    "starter_validation": True,
                    "invalid_command_exit": 2,
                }
            )
        )


if __name__ == "__main__":
    main()
