param(
  [Parameter(Mandatory = $true)]
  [string]$KeyName,

  [string]$Comment = ""
)

$ErrorActionPreference = "Stop"

$sshDir = Join-Path $env:USERPROFILE ".ssh"
$keyPath = Join-Path $sshDir "id_ed25519_$KeyName"
$pubPath = "$keyPath.pub"

if (-not (Test-Path $sshDir)) {
  New-Item -ItemType Directory -Path $sshDir | Out-Null
}

if (Test-Path $keyPath) {
  Write-Error "Key already exists: $keyPath — remove it first or pick another KeyName."
  exit 1
}

$c = if ($Comment) { $Comment } else { "GitHub $KeyName on $env:COMPUTERNAME" }

Write-Host "Generating: $keyPath"
ssh-keygen -t ed25519 -C $c -f $keyPath

Write-Host ""
Write-Host "=== Add this PUBLIC key to GitHub → Settings → SSH and GPG keys ==="
Get-Content $pubPath
Write-Host ""
Write-Host "Then add a Host block to $sshDir\config pointing IdentityFile to:"
Write-Host "  $keyPath"
