$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"

if (-not (Test-Path (Join-Path $backend ".venv\Scripts\python.exe"))) {
  throw "Backend venv not found. Run setup first."
}

$env:JETSPACE_CLEANUP_DRY_RUN = "true"
$env:JETSPACE_CLEANUP_MIN_AGE_HOURS = "24"
$env:JETSPACE_CLEANUP_MAX_DELETE_MB = "2048"
$env:JETSPACE_CLEANUP_MAX_ITEMS = "500"

Set-Location $backend
.\.venv\Scripts\python scripts\cleanup_once.py
