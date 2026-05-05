$ErrorActionPreference = "Stop"

Write-Host "== Jetspace Secure Harmonize =="

$project = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $project "backend"
$env:JETSPACE_ROOT = $project

# 1) Enforce localhost-only bind for control API 8010
$lines = netstat -ano | Select-String "LISTENING" | Where-Object { $_.Line -match ":8010\s" }
$badPids = @()
foreach ($m in $lines) {
  $line = $m.Line.Trim()
  if ($line -match "0\.0\.0\.0:8010\s+\S+\s+LISTENING\s+(\d+)$") {
    $badPids += [int]$Matches[1]
  }
}
$badPids = $badPids | Select-Object -Unique
foreach ($procId in $badPids) {
  Write-Host "Stopping non-local 8010 listener PID $procId"
  taskkill /PID $procId /T /F | Out-Null
}

# 2) Start/ensure localhost-bound 8010 API
Write-Host "Starting localhost-bound control API on 127.0.0.1:8010"
Start-Process powershell -WindowStyle Hidden -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-Command","cd '$backend'; .\.venv\Scripts\python -m uvicorn app:app --host 127.0.0.1 --port 8010"

Start-Sleep -Seconds 2

# 3) Trigger bounded cleanup apply only through guarded policy
Write-Host "Running bounded maintenance apply (guarded by load gates)"
& (Join-Path $project "scripts\maintenance-weekly.ps1")

# 4) Generate fresh security and harmony reports
Write-Host "Generating reports..."
& (Join-Path $project "scripts\security-checkpoints.ps1")
$wslUnix = ""
try {
  $wslUnix = (wsl wslpath -u $project).Trim()
} catch {
  $wslUnix = ""
}
if ([string]::IsNullOrWhiteSpace($wslUnix)) {
  $drive = $project.Substring(0, 1).ToLower()
  $tail = $project.Substring(2) -replace '\\', '/'
  $wslUnix = "/mnt/$drive$tail"
}
$audit = "cd '$wslUnix' && export JETSPACE_ROOT=`"$wslUnix`" && bash scripts/wsl-harmony-audit.sh"
$diag = "cd '$wslUnix' && export JETSPACE_ROOT=`"$wslUnix`" && bash scripts/wsl-modal-network-diagnose.sh"
wsl -d Ubuntu -e bash -lc $audit | Out-Null
wsl -d Ubuntu -e bash -lc $diag | Out-Null

Write-Host "Complete. Reports at $(Join-Path $project 'reports')"
