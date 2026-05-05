# Add or update the "mirror" remote for a second GitHub account (e.g. invasivejet).
# Use an SSH Host alias when you have two keys (see AGENTS.md).
param(
    [string] $SshHostAlias = "github.com-ij",
    [string] $Owner = "invasivejet",
    [string] $Repo = "jetspace-monitor"
)
$ErrorActionPreference = "Stop"
$url = "git@${SshHostAlias}:${Owner}/${Repo}.git"
$hasMirror = git remote 2>$null | Select-String -Pattern "^mirror$" -Quiet
if ($hasMirror) {
    git remote set-url mirror $url
    Write-Host "Updated mirror -> $url"
}
else {
    git remote add mirror $url
    Write-Host "Added mirror -> $url"
}
git remote -v
