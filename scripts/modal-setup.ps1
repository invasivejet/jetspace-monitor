param(
  [switch]$SkipSecret
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$env:JETSPACE_ROOT = $projectRoot

Write-Host "== Jetspace Modal setup (Windows) =="
Write-Host "Repository: $projectRoot"

Write-Host "[1/6] Installing Modal client..."
python -m pip install --user --upgrade modal

Write-Host "[2/6] Browser authentication (modal setup)..."
python -m modal setup

Write-Host "[3/6] Active profile..."
modal profile current

if (-not $SkipSecret) {
  Write-Host "[4/6] Secret: custom-secret, key jetspace (value not echoed)..."
  $secure = Read-Host "Enter value for custom-secret[jetspace]" -AsSecureString
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
  try {
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    modal secret create custom-secret "jetspace=$plain" --force
  } finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  }
} else {
  Write-Host "[4/6] Skipping secret (--SkipSecret)."
}

Write-Host "[5/6] CPU worker examples..."
modal run (Join-Path $projectRoot "modal\get_started.py")
modal run (Join-Path $projectRoot "modal\secret_probe.py")

Write-Host "[6/6] Runtime telemetry (GPU worker may skip if unavailable)..."
modal run (Join-Path $projectRoot "modal\runtime_telemetry.py")
if ($LASTEXITCODE -ne 0) {
  Write-Host "runtime_telemetry exited $LASTEXITCODE (optional; GPU quota or CLI issue)."
}

Write-Host "Done. Contract: GET http://127.0.0.1:8010/modal/workflow (with API running)."
