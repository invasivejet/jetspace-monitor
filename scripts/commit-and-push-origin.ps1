param(
  [Parameter(Mandatory = $true)]
  [string]$Message,

  [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\Find-Git.ps1"
$git = Get-JetspaceGitExe
if (-not $git) {
  Write-Error "git.exe not found. Install Git for Windows: https://git-scm.com/download/win then re-open PowerShell."
  exit 2
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
  Write-Host "Using: $git"
  & $git status
  & $git add -A
  & $git diff --cached --quiet
  if ($LASTEXITCODE -eq 0) {
    Write-Host "No changes to commit."
    exit 0
  }
  & $git diff --cached --stat
  & $git commit -m $Message
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "commit failed (exit $LASTEXITCODE)."
    exit $LASTEXITCODE
  }
  & $git push -u origin $Branch
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
