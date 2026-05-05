$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"

if (-not (Test-Path (Join-Path $backend ".venv\Scripts\python.exe"))) {
  throw "Backend venv not found. Run setup first."
}

# Conservative defaults for reliability.
$env:JETSPACE_CLEANUP_MIN_AGE_HOURS = "36"
$env:JETSPACE_CLEANUP_MAX_DELETE_MB = "1024"
$env:JETSPACE_CLEANUP_MAX_ITEMS = "300"
$env:JETSPACE_CLEANUP_MAX_CPU_PERCENT = "65"
$env:JETSPACE_CLEANUP_MAX_RAM_PERCENT = "78"
$env:JETSPACE_CLEANUP_MIN_FREE_DISK_GB = "6"

Set-Location $backend
.\.venv\Scripts\python scripts\auto_maintenance.py --tag daily-plan
