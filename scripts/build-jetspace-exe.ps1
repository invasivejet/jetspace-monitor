param(
  [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $repoRoot "backend"
$venvPy = Join-Path $backend ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPy)) {
  Write-Error "Backend venv missing. Run: cd backend; python -m venv .venv; .\\.venv\\Scripts\\pip install -r requirements.txt"
  exit 1
}

if (-not $SkipFrontend) {
  $fe = Join-Path $repoRoot "frontend"
  Push-Location $fe
  try {
    if (-not (Test-Path "node_modules")) { npm install }
    npm run build
  } finally {
    Pop-Location
  }
}

Write-Host "[pyinstaller] Installing build tool if needed..."
& $venvPy -m pip install "pyinstaller>=6.0"

Push-Location $backend
try {
  Write-Host "[pyinstaller] Building onedir bundle (JetspaceMonitor.exe)..."
  & $venvPy -m PyInstaller --noconfirm --clean --onedir --name JetspaceMonitor `
    jetspace_desktop.py `
    --collect-all uvicorn `
    --collect-all fastapi `
    --collect-all starlette `
    --collect-all pydantic `
    --collect-all psutil `
    --collect-all cryptography

  $out = Join-Path $backend "dist\JetspaceMonitor"
  Write-Host ""
  Write-Host "Done. Run:"
  Write-Host "  $out\JetspaceMonitor.exe"
  Write-Host "Copies secrets/ and data/ next to the exe if you use the bridge journal (create locally; never commit)."
} finally {
  Pop-Location
}
