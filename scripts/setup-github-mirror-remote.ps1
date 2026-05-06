# Add or update a second remote (default name: mirror) for another GitHub namespace.
# Use an SSH Host alias when you have two keys (see AGENTS.md).
param(
    [string] $SshHostAlias = "github.com-ij",
    [string] $Owner = "invasivejet",
    [string] $Repo = "jetspace-monitor",
    [string] $RemoteName = "mirror"
)
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\Find-Git.ps1"
$git = Get-JetspaceGitExe
if (-not $git) {
    Write-Error "git.exe not found. Install Git for Windows: https://git-scm.com/download/win"
    exit 2
}
$repoRoot = Split-Path -Parent $PSScriptRoot
$url = "git@${SshHostAlias}:${Owner}/${Repo}.git"
Push-Location $repoRoot
try {
    $has = & $git remote 2>$null | Select-String -Pattern "^${RemoteName}$" -Quiet
    if ($has) {
        & $git remote set-url $RemoteName $url
        Write-Host "Updated $RemoteName -> $url"
    }
    else {
        & $git remote add $RemoteName $url
        Write-Host "Added $RemoteName -> $url"
    }
    & $git remote -v
} finally {
    Pop-Location
}
