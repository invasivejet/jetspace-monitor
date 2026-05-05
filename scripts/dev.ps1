param(
  [switch]$Install
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"
$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"

if ($Install -or -not (Test-Path $venvPython)) {
  Write-Host "[backend] Creating venv + installing dependencies..."
  python -m venv (Join-Path $backendDir ".venv")
  & $venvPython -m pip install --upgrade pip
  & $venvPython -m pip install -r (Join-Path $backendDir "requirements.txt")
}

Write-Host "[backend] Starting API server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; ..\.venv\Scripts\python -m uvicorn app:app --host 127.0.0.1 --port 8010"

if ($Install -or -not (Test-Path (Join-Path $frontendDir "node_modules"))) {
  Write-Host "[frontend] Installing dependencies..."
  Push-Location $frontendDir
  npm install
  Pop-Location
}

Write-Host "[frontend] Starting UI server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm run dev -- --host 127.0.0.1 --port 5173"

Write-Host "Started:"
Write-Host "- API: http://127.0.0.1:8010"
Write-Host "- UI:  http://127.0.0.1:5173/index.html"
