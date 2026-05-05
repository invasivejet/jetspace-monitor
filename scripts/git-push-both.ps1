# Push current branch to both GitHub remotes (origin + mirror).
# Requires: git remote "origin" (joel-saucedo) and "mirror" (invasivejet) configured.
param(
    [string] $Branch = ""
)
$ErrorActionPreference = "Stop"
if (-not $Branch) {
    $Branch = (git rev-parse --abbrev-ref HEAD).Trim()
}
Write-Host "Pushing $Branch to origin..."
git push origin $Branch
Write-Host "Pushing $Branch to mirror..."
git push mirror $Branch
Write-Host "Done."
