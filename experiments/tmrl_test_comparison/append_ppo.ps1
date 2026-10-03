param(
    [Parameter(Mandatory=$true)][int]$QueueProcessId,
    [Parameter(Mandatory=$true)][string]$QueueDirectory
)
$ErrorActionPreference = 'Stop'
Wait-Process -Id $QueueProcessId -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath (Join-Path $QueueDirectory 'STOP')) { exit 0 }
$history = @(Get-Content -LiteralPath (Join-Path $QueueDirectory 'history.jsonl') | ForEach-Object { $_ | ConvertFrom-Json })
foreach ($algorithm in @('iqn', 'qr', 'discrete-sac', 'tqc')) {
    $completed = @($history | Where-Object { $_.algorithm -eq $algorithm -and $_.status -eq 'completed' -and $_.returncode -eq 0 })
    if ($completed.Count -ne 1) { throw "PPO skipped: $algorithm did not complete successfully." }
}
if (@($history | Where-Object { $_.algorithm -eq 'ppo' }).Count -gt 0) { exit 0 }
$repository = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location -LiteralPath $repository
& (Join-Path $repository '.venv/Scripts/python.exe') -u -m experiments.tmrl_test_comparison.run_pilots $QueueDirectory ppo
exit $LASTEXITCODE
