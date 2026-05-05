$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"

if (-not (Test-Path (Join-Path $backend ".venv\Scripts\python.exe"))) {
  throw "Backend venv not found. Run setup first."
}

# Weekly bounded apply with strict pressure guards.
$env:JETSPACE_CLEANUP_MIN_AGE_HOURS = "72"
$env:JETSPACE_CLEANUP_MAX_DELETE_MB = "512"
$env:JETSPACE_CLEANUP_MAX_ITEMS = "150"
$env:JETSPACE_CLEANUP_MAX_CPU_PERCENT = "60"
$env:JETSPACE_CLEANUP_MAX_RAM_PERCENT = "75"
$env:JETSPACE_CLEANUP_MIN_FREE_DISK_GB = "8"

Set-Location $backend
.\.venv\Scripts\python scripts\auto_maintenance.py --apply --tag weekly-apply
