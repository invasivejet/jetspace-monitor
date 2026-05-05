$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$dailyScript = Join-Path $projectRoot "scripts\maintenance-daily.ps1"
$weeklyScript = Join-Path $projectRoot "scripts\maintenance-weekly.ps1"

if (-not (Test-Path $dailyScript) -or -not (Test-Path $weeklyScript)) {
  throw "Maintenance scripts missing."
}

$dailyTask = "Jetspace-Maintenance-Daily-Plan"
$weeklyTask = "Jetspace-Maintenance-Weekly-Apply"
$dailyCmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$dailyScript`""
$weeklyCmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$weeklyScript`""

schtasks /Create /TN $dailyTask /TR $dailyCmd /SC DAILY /ST 03:10 /RL LIMITED /F | Out-Null
schtasks /Create /TN $weeklyTask /TR $weeklyCmd /SC WEEKLY /D SUN /ST 03:30 /RL LIMITED /F | Out-Null

Write-Host "Scheduled tasks configured:"
Write-Host "- $dailyTask (daily dry-run style plan)"
Write-Host "- $weeklyTask (weekly bounded apply if pressure is safe)"
