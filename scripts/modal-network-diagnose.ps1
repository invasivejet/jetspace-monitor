$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$env:JETSPACE_ROOT = $projectRoot
$backend = Join-Path $projectRoot "backend"
$venvPy = Join-Path $backend ".venv\Scripts\python.exe"

$py = if (Test-Path $venvPy) { $venvPy } else { "python" }

Write-Host "== Modal network diagnose (local shell) =="
Push-Location $backend
try {
  & $py "scripts\modal_network_diagnose.py"
} finally {
  Pop-Location
}
