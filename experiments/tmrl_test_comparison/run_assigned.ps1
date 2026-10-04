param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('iqn', 'qr', 'discrete-sac', 'tqc', 'ppo', 'sac')]
    [string]$Algorithm,
    [switch]$Pilot
)
$ErrorActionPreference = 'Stop'
if (-not $Pilot -and $Algorithm -eq 'discrete-sac') {
    throw 'DSAC nie jest gotowy do pelnych treningow. Najpierw pilot celu entropii 2.0 i ewaluacja; patrz READINESS.md. Test: run_assigned.ps1 discrete-sac -Pilot.'
}
$comparisonMutex = [System.Threading.Mutex]::new($false, 'Global\TrackmaniaRL.ComparisonController')
$comparisonMutexAcquired = $false
try {
    try { $comparisonMutexAcquired = $comparisonMutex.WaitOne(0) }
    catch [System.Threading.AbandonedMutexException] { $comparisonMutexAcquired = $true }
    if (-not $comparisonMutexAcquired) {
        throw 'Inny launcher posiada blokade sterowania gra. Kolejka nie zostala uruchomiona.'
    }
$comparisonRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location -LiteralPath $comparisonRoot
$comparisonPython = Join-Path $comparisonRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $comparisonPython)) { throw 'Najpierw uruchom uv sync --group dev.' }
$comparisonStop = Join-Path $comparisonRoot "artifacts/STOP-$Algorithm"
function Assert-ComparisonIdle {
    $comparisonBusy = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
        Where-Object {
            $_.CommandLine -match 'trackmaniarl\s+(train|resume|benchmark)\b' -or
            $_.CommandLine -match 'tmrl_test_comparison\.launch_checks\s+benchmark\b' -or
            $_.CommandLine -match '--comparison-map-preflight' -or
            $_.CommandLine -match 'runtime_helper\.py.*\bpreflight\b'
        }
    if ($comparisonBusy) { throw 'Inny trening lub ewaluacja steruje gra. Poczekaj na jego zakonczenie.' }
}
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
run_dir = (path.parent / spec.artifacts_dir / spec.run_id).resolve()
if run_dir.exists():
    raise RuntimeError(f'Run already exists: {run_dir}. Resume its checkpoint explicitly.')
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
'@ | & $comparisonPython - $ConfigPath --comparison-map-preflight
    if ($LASTEXITCODE -ne 0) { throw 'Mapa nie jest gotowa. Trening nie zostal uruchomiony.' }
}
$comparisonSeeds = if ($Pilot) { @(17) } else { @(17, 29, 43) }
foreach ($comparisonSeed in $comparisonSeeds) {
    if (Test-Path -LiteralPath $comparisonStop) { break }
    Assert-ComparisonIdle
    $comparisonStage = if ($Pilot) { 'pilot' } else { 'full' }
    $comparisonConfig = "experiments/tmrl_test_comparison/configs/$comparisonStage/$Algorithm-s$comparisonSeed.yaml"
    if ($Pilot -and $Algorithm -eq 'discrete-sac') {
        $comparisonConfig = 'experiments/tmrl_test_comparison/configs/diagnostic/discrete-sac-entropy200-beta000-s17.yaml'
    }
    if (Test-Path -LiteralPath $comparisonStop) { break }
    Initialize-ComparisonMap $comparisonConfig
    if (Test-Path -LiteralPath $comparisonStop) { break }
    Assert-ComparisonIdle
    $comparisonTrainArgs = @('-m', 'trackmaniarl', 'train', $comparisonConfig, '--stop-file', $comparisonStop)
    & $comparisonPython @comparisonTrainArgs
    if ($LASTEXITCODE -ne 0) { throw "Trening $Algorithm seed $comparisonSeed nie powiodl sie. Kolejka zatrzymana." }
    if (Test-Path -LiteralPath $comparisonStop) { break }
    if (-not $Pilot) {
        $comparisonCheckpoint = & $comparisonPython -m experiments.tmrl_test_comparison.launch_checks checkpoint $comparisonConfig
        if ($LASTEXITCODE -ne 0) { throw 'Brak potwierdzonego koncowego checkpointu. Wznow trening jawnie; kolejka zatrzymana.' }
        $comparisonCheckpoint = ($comparisonCheckpoint | Out-String).Trim()
        if (Test-Path -LiteralPath $comparisonStop) { break }
        if ($Algorithm -eq 'ppo') {
            # PPO's trainer already evaluated exactly 30 trials after the final save.
            # Validate that measurement instead of silently collecting another 30.
            & $comparisonPython -m experiments.tmrl_test_comparison.launch_checks evaluation $comparisonConfig $comparisonCheckpoint
        } else {
            Assert-ComparisonIdle
            if (Test-Path -LiteralPath $comparisonStop) { break }
            & $comparisonPython -m experiments.tmrl_test_comparison.launch_checks benchmark $comparisonConfig $comparisonCheckpoint --stop-file $comparisonStop
        }
        if ($LASTEXITCODE -ne 0) { throw 'Ewaluacja nie jest kompletnym poprawnym pomiarem 30 prob. Kolejka zatrzymana; zachowano artefakty.' }
    }
}
} finally {
    if ($comparisonMutexAcquired) { $comparisonMutex.ReleaseMutex() }
    $comparisonMutex.Dispose()
}
