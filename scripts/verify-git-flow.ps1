# Validates local clone is wired for invasivejet as canonical origin (run after set-origin-invasivejet.ps1).
# Does NOT push, pull, or overwrite remotes.

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

. "$PSScriptRoot\Find-Git.ps1"
$git = Get-JetspaceGitExe
if (-not $git) {
  Write-Error "git.exe not found. Install Git for Windows: https://git-scm.com/download/win"
  exit 2
}

Push-Location $repoRoot
try {
  $origin = (& $git remote get-url origin 2>$null)
  if (-not $origin) {
    Write-Error "No 'origin' remote. Run: .\scripts\set-origin-invasivejet.ps1"
    exit 1
  }

  $ok = $false
  if ($origin -match "invasivejet/jetspace-monitor") { $ok = $true }
  if ($origin -match "git@.*:invasivejet/jetspace-monitor\.git") { $ok = $true }

  if (-not $ok) {
    Write-Error "origin should point to invasivejet/jetspace-monitor. Current: $origin"
    exit 1
  }

  if ($origin -match '^git@github\.com:') {
    Write-Warning "origin uses git@github.com: (default SSH host). With two GitHub accounts, SSH often picks the wrong key and push fails with 'denied to joel-saucedo'."
    Write-Warning "Fix: run .\scripts\set-origin-invasivejet.ps1 (uses github.com-ij by default) or:"
    Write-Warning "  git remote set-url origin git@github.com-ij:invasivejet/jetspace-monitor.git"
    Write-Warning "Ensure ~/.ssh/config has Host github.com-ij with IdentityFile for invasivejet."
  }

  Write-Host "OK: origin -> $origin"
  Write-Host ""
  Write-Host "All remotes:"
  & $git remote -v
  Write-Host ""
  Write-Host "Reachability (read-only):"
  & $git ls-remote origin HEAD
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "git ls-remote failed (SSH key, network, or repo empty). Fix SSH then retry."
    exit 1
  }

  Write-Host ""
  Write-Host "Next: git pull origin main && git push origin main"
  exit 0
} finally {
  Pop-Location
}
