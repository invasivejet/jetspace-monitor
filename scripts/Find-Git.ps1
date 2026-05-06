# Shared helper: resolve git.exe on Windows (many installs omit PATH in automation shells).
function Get-JetspaceGitExe {
  $candidates = @(
    (Get-Command git.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
    "$env:ProgramFiles\Git\cmd\git.exe",
    "$env:ProgramFiles\Git\bin\git.exe",
    "${env:ProgramFiles(x86)}\Git\cmd\git.exe"
  ) | Where-Object { $_ -and (Test-Path $_) }
  if ($candidates) { return $candidates[0] }
  return $null
}
