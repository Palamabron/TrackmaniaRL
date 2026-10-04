"""Launcher guards must stop before opening a live game controller."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from trackmaniarl.core.spec import RunSpec


def test_preflight_refuses_existing_run_before_creating_controller(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    launcher = (
        Path(__file__).resolve().parents[3] / "experiments/tmrl_test_comparison/run_assigned.ps1"
    )
    text = launcher.read_text(encoding="utf-8")
    preflight = text.split("@'", 1)[1].split("'@", 1)[0]
    existing = tmp_path / "artifacts" / "existing"
    existing.mkdir(parents=True)
    spec = SimpleNamespace(artifacts_dir=tmp_path / "artifacts", run_id="existing")
    monkeypatch.setattr(RunSpec, "from_yaml", lambda _: spec)
    monkeypatch.setattr(sys, "argv", ["preflight", str(tmp_path / "config.yaml")])
    with pytest.raises(RuntimeError, match="Run already exists"):
        exec(compile(preflight, "comparison-preflight", "exec"), {})


def test_comparison_launcher_rejects_unqualified_runs_and_busy_game(tmp_path: Path) -> None:
    shell = shutil.which("powershell.exe")
    if shell is None:
        pytest.skip("Windows launcher requires PowerShell")
    launcher = (
        Path(__file__).resolve().parents[3] / "experiments/tmrl_test_comparison/run_assigned.ps1"
    )
    script = tmp_path / "guards.ps1"
    script.write_text(
        r"""
param([string]$Launcher)
$ErrorActionPreference = 'Stop'
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $Launcher, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Launcher syntax is invalid' }
foreach ($algorithm in @('discrete-sac', 'sac')) {
    $blocked = $false
    try { & $Launcher $algorithm } catch { $blocked = $_.Exception.Message -match 'pelnych|Pelne' }
    if (-not $blocked) { throw "Unqualified algorithm was not blocked: $algorithm" }
}
$guard = $ast.Find({ param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
    $node.Name -eq 'Assert-ComparisonIdle'
}, $true)
. ([scriptblock]::Create($guard.Extent.Text))
function Get-CimInstance { param($ClassName, $Filter) @() }
Assert-ComparisonIdle
function Get-CimInstance { param($ClassName, $Filter)
    [pscustomobject]@{CommandLine = 'python.exe -m trackmaniarl train config.yaml'}
}
$blocked = $false
try { Assert-ComparisonIdle } catch { $blocked = $_.Exception.Message -match 'steruje gra' }
if (-not $blocked) { throw 'Active controller was not blocked' }
Write-Output 'Launcher guards passed without game input'
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), str(launcher)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Launcher guards passed" in result.stdout
