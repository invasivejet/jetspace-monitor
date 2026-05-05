$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"

Set-Location $backend
.\.venv\Scripts\python scripts\minimon_agent.py
