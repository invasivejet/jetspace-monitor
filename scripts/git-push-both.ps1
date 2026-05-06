param(
  [string]$Branch = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $projectRoot
try {
  $target = if ($Branch) { $Branch } else { (& git rev-parse --abbrev-ref HEAD).Trim() }
  Write-Host "Pushing branch: $target"

  git remote get-url origin 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Remote 'origin' is not configured."
    exit 1
  }
  git remote get-url mirror 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Remote 'mirror' is not configured. Run: .\scripts\setup-github-mirror-remote.ps1 -SshHostAlias github.com-ij"
    exit 1
  }

  git push -u origin $target
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

  git push -u mirror $target
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
