<# Run one command on selected logical CPUs, restoring the caller afterward. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [int[]] $Cpu,
    [Parameter(Mandatory = $true)]
    [string] $Executable,
    [string[]] $Arguments = @()
)

$ErrorActionPreference = 'Stop'
$taskProcess = [System.Diagnostics.Process]::GetCurrentProcess()
$taskOriginalAffinity = $taskProcess.ProcessorAffinity
$taskMask = [long]0
foreach ($taskCpu in $Cpu) {
    if ($taskCpu -lt 0 -or $taskCpu -ge [Math]::Min(63, [Environment]::ProcessorCount)) {
        throw "Invalid logical CPU index: $taskCpu"
    }
    $taskMask = $taskMask -bor ([long]1 -shl $taskCpu)
}
if ($taskMask -eq 0 -or ($taskMask -band $taskOriginalAffinity.ToInt64()) -ne $taskMask) {
    throw 'Select at least one CPU allowed by the current process affinity.'
}
$taskCommand = Get-Command -Name $Executable -CommandType Application -ErrorAction Stop
try {
    $taskProcess.ProcessorAffinity = [IntPtr]$taskMask
    & $taskCommand.Source @Arguments
    $taskExitCode = $LASTEXITCODE
} finally {
    $taskProcess.ProcessorAffinity = $taskOriginalAffinity
}
exit $taskExitCode
