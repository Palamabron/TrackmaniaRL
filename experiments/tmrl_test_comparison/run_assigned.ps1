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
foreach ($comparisonSeed in @(17, 29, 43)) {
    if (Test-Path -LiteralPath $comparisonStop) { break }
    & $comparisonPython -m trackmaniarl train "experiments/tmrl_test_comparison/configs/full/$Algorithm-s$comparisonSeed.yaml" --stop-file $comparisonStop
    if ($LASTEXITCODE -ne 0) { throw "Trening $Algorithm seed $comparisonSeed nie powiodl sie. Kolejka zatrzymana." }
}
