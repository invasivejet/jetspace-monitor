param(
  [Parameter(Mandatory = $true)]
  [string]$KeyTag
)

$ErrorActionPreference = "Stop"

# This file must live in the jetspace-monitor repo root. Run:
#   cd C:\Users\<you>\jetspace-monitor
#   .\Run-WslSshKeygen.ps1 -KeyTag joel

$repoRoot = $PSScriptRoot
$launcher = Join-Path $repoRoot "ssh-keygen-wsl.sh"
if (-not (Test-Path $launcher)) {
  Write-Error "Expected $launcher — place this script in the jetspace-monitor repo root."
  exit 1
}

$unixRepo = (wsl wslpath -u $repoRoot).Trim()
if (-not $unixRepo) {
  Write-Error "Could not convert path to WSL (is WSL installed?). Path: $repoRoot"
  exit 1
}

Write-Host "Using WSL bash + repo: $unixRepo"
wsl.exe -e bash -lc "'$unixRepo/ssh-keygen-wsl.sh' '$KeyTag'"
