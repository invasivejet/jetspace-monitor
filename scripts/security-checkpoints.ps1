$ErrorActionPreference = "Stop"

Write-Host "== Jetspace Security Checkpoints =="

# 1) Port exposure checkpoints (localhost-only expected for control services)
$ports = @(8000, 8010, 8443, 5173)
$listening = netstat -ano | Select-String "LISTENING"
$violations = @()
foreach ($p in $ports) {
  $matches = $listening | Where-Object { $_.Line -match "[:\.]$p\s" }
  foreach ($m in $matches) {
    $line = $m.Line.Trim()
    if ($line -notmatch "127\.0\.0\.1:$p") {
      $violations += "Port $p not localhost-only: $line"
    }
  }
}

# 2) Startup persistence checkpoints
$startup = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$expectedStartup = @(
  "jetspace-control-runtime.cmd",
  "jetspace-minimon-startup.cmd"
)
$missingStartup = @()
foreach ($f in $expectedStartup) {
  if (-not (Test-Path (Join-Path $startup $f))) {
    $missingStartup += $f
  }
}

# 3) Scheduled tasks checkpoints
$tasks = @("Jetspace-Maintenance-Daily-Plan", "Jetspace-Maintenance-Weekly-Apply")
$taskStatus = @()
foreach ($t in $tasks) {
  $q = schtasks /Query /TN $t /V /FO LIST 2>$null
  if ($LASTEXITCODE -ne 0) {
    $taskStatus += "MISSING: $t"
  } else {
    $state = ($q | Select-String "^Scheduled Task State").ToString()
    $last = ($q | Select-String "^Last Result").ToString()
    $taskStatus += "$t | $state | $last"
  }
}

# 4) Secret hygiene checkpoints (best-effort checks only; no secrets printed)
$secretFiles = Get-ChildItem -Path "C:\Users\joela\jetspace-monitor" -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match "\.env|secret|token|key" -and $_.FullName -notmatch "\\\.venv\\" }

$summary = [ordered]@{
  generated_at = (Get-Date).ToString("s")
  port_violations = $violations
  missing_startup_items = $missingStartup
  task_status = $taskStatus
  potential_secret_files = ($secretFiles | Select-Object -ExpandProperty FullName)
}

$reportDir = "C:\Users\joela\jetspace-monitor\reports"
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
$out = Join-Path $reportDir ("security-checkpoints-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".json")
$summary | ConvertTo-Json -Depth 5 | Set-Content $out

Write-Host "Report written:" $out
if ($violations.Count -gt 0) {
  Write-Host "Port violations detected:" -ForegroundColor Yellow
  $violations | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
}
if ($missingStartup.Count -gt 0) {
  Write-Host "Missing startup items:" -ForegroundColor Yellow
  $missingStartup | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
}
Write-Host "Done."
