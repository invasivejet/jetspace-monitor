param(
  [Parameter(Mandatory = $true)]
  [string]$SshHostAlias,

  [string]$Owner = "invasivejet",
  [string]$Repo = "jetspace-monitor",
  [string]$RemoteName = "mirror"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$repoUrl = "git@${SshHostAlias}:${Owner}/${Repo}.git"

Push-Location $projectRoot
try {
  $hasRemote = $false
  git remote get-url $RemoteName 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { $hasRemote = $true }

  if ($hasRemote) {
    Write-Host "Updating remote '$RemoteName' -> $repoUrl"
    git remote set-url $RemoteName $repoUrl
  } else {
    Write-Host "Adding remote '$RemoteName' -> $repoUrl"
    git remote add $RemoteName $repoUrl
  }

  Write-Host ""
  git remote -v
} finally {
  Pop-Location
}
