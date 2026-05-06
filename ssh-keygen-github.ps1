param(
  [Parameter(Mandatory = $true)]
  [string]$KeyName,

  [string]$Comment = ""
)

$ErrorActionPreference = "Stop"
$inner = Join-Path $PSScriptRoot "scripts\ssh-keygen-github.ps1"
if (-not (Test-Path $inner)) {
  Write-Error "Expected script missing: $inner — run from jetspace-monitor repo root."
  exit 1
}
& $inner -KeyName $KeyName -Comment $Comment
