param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('iqn', 'qr', 'discrete-sac', 'tqc', 'ppo')]
    [string]$Algorithm
)
$ErrorActionPreference = 'Stop'
$comparisonRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location -LiteralPath $comparisonRoot
$comparisonPython = Join-Path $comparisonRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $comparisonPython)) { throw 'Najpierw uruchom uv sync --group dev.' }
$comparisonStop = Join-Path $comparisonRoot "artifacts/STOP-$Algorithm"
function Initialize-ComparisonMap([string]$ConfigPath) {
    # A completed validation lap has no live telemetry until the map is restarted.
    # This short-lived controller exits before the training process starts.
    @'
import sys
import time
from pathlib import Path
from trackmaniarl.core.spec import RunSpec
from trackmaniarl.trackmania.environment import OpenPlanetEnvironmentFactory

path = Path(sys.argv[1]).resolve()
spec = RunSpec.from_yaml(path)
component = spec.components.environment
if component.class_path != 'trackmaniarl.trackmania.environment:OpenPlanetEnvironmentFactory':
    raise RuntimeError('Comparison preflight requires the first-party Trackmania environment')
factory = OpenPlanetEnvironmentFactory(**component.kwargs, base_dir=path.parent)
environment = factory.create(seed=spec.seed)
try:
    uid = environment.config.expected_map_uid
    environment._session.verify_loaded_map(uid)
    environment.controller.confirm_finish()
    time.sleep(0.5)
    environment.controller.reset()
    time.sleep(1.0)
    environment.client.read()
    environment._session.confirm_ready(uid)
    print('Comparison map ready:', uid, flush=True)
finally:
    environment.close()
'@ | & $comparisonPython - $ConfigPath
    if ($LASTEXITCODE -ne 0) { throw 'Mapa nie jest gotowa. Trening nie zostal uruchomiony.' }
}
foreach ($comparisonSeed in @(17, 29, 43)) {
    if (Test-Path -LiteralPath $comparisonStop) { break }
    $comparisonConfig = "experiments/tmrl_test_comparison/configs/full/$Algorithm-s$comparisonSeed.yaml"
    Initialize-ComparisonMap $comparisonConfig
    if (Test-Path -LiteralPath $comparisonStop) { break }
    & $comparisonPython -m trackmaniarl train $comparisonConfig --stop-file $comparisonStop
    if ($LASTEXITCODE -ne 0) { throw "Trening $Algorithm seed $comparisonSeed nie powiodl sie. Kolejka zatrzymana." }
}
