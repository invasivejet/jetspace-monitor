param(
  [string]$SshHostAlias = "github.com-ij",
  [string]$Owner = "invasivejet",
  [string]$Repo = "jetspace-monitor",
  [string]$BackupRemoteName = "joel-saucedo"
)

# Previous origin (e.g. joel-saucedo/jetspace-monitor) is stored under BackupRemoteName.

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\Find-Git.ps1"
$git = Get-JetspaceGitExe
if (-not $git) {
  Write-Error "git.exe not found. Install Git for Windows: https://git-scm.com/download/win"
  exit 2
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$newUrl = "git@${SshHostAlias}:${Owner}/${Repo}.git"

Push-Location $repoRoot
try {
  $hadOrigin = $false
  $oldUrl = ""
  try {
    $oldUrl = (& $git remote get-url origin 2>$null).Trim()
    if ($oldUrl) { $hadOrigin = $true }
  } catch { }

  if ($hadOrigin -and $oldUrl -and ($oldUrl -ne $newUrl)) {
    if ($oldUrl -notmatch [regex]::Escape($Owner)) {
      Write-Host "Preserving previous origin as remote '$BackupRemoteName' -> $oldUrl"
      & $git remote remove $BackupRemoteName 2>$null
      & $git remote add $BackupRemoteName $oldUrl
    }
  }

  if (-not $hadOrigin) {
    & $git remote add origin $newUrl
  } else {
    & $git remote set-url origin $newUrl
  }

  & $git config push.default simple
  Write-Host ""
  Write-Host "origin is now: $newUrl"
  Write-Host "Remotes:"
  & $git remote -v
  Write-Host ""
  Write-Host "Next: ssh -T git@${SshHostAlias}  (must show invasivejet)"
  Write-Host "Then: git push -u origin main"
} finally {
  Pop-Location
}
