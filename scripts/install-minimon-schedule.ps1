$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $projectRoot "scripts\run-minimon.ps1"
if (-not (Test-Path $runner)) { throw "run-minimon.ps1 missing" }

$taskName = "Jetspace-Minimon-Airgap-Local"
$cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$runner`""

schtasks /Create /TN $taskName /TR $cmd /SC ONLOGON /RL LIMITED /F | Out-Null
if ($LASTEXITCODE -ne 0) {
  throw "Failed to create scheduled task ($taskName). Try running PowerShell as Administrator."
}
Write-Host "Scheduled task configured: $taskName"
