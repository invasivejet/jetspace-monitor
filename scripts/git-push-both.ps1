# Push current branch to primary + secondary GitHub remotes.
# Canonical layout (see docs/GITHUB-REMOTES-AND-ORGS.md):
#   origin       -> invasivejet/jetspace-monitor (day-to-day)
#   joel-saucedo -> legacy copy on joel-saucedo (if set by set-origin-invasivejet.ps1)
# Alternate: remote named "mirror" is pushed if joel-saucedo is absent.
param(
    [string] $Branch = ""
)
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\Find-Git.ps1"
$git = Get-JetspaceGitExe
if (-not $git) {
    Write-Error "git.exe not found. Install Git for Windows: https://git-scm.com/download/win"
    exit 2
}
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if (-not $Branch) {
        $Branch = (& $git rev-parse --abbrev-ref HEAD).Trim()
    }
    Write-Host "Pushing $Branch to origin..."
    & $git push origin $Branch
    $secondary = $null
    $urls = (& $git remote 2>$null)
    if ($urls -contains "joel-saucedo") { $secondary = "joel-saucedo" }
    elseif ($urls -contains "mirror") { $secondary = "mirror" }
    if ($secondary) {
        Write-Host "Pushing $Branch to $secondary..."
        & $git push $secondary $Branch
    }
    else {
        Write-Host "No secondary remote (joel-saucedo or mirror). Only origin was pushed."
        Write-Host "To add legacy remote: run set-origin-invasivejet.ps1 once (it preserves joel-saucedo)."
    }
    Write-Host "Done."
} finally {
    Pop-Location
}
