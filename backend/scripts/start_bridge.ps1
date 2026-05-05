$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

$env:JETSPACE_BRIDGE_SHARED_SECRET = "change-this-shared-secret"

Write-Host "Generating certs..."
& "$root\.venv\Scripts\python.exe" "$root\scripts\generate_certs.py"

Write-Host "Starting mTLS bridge on https://127.0.0.1:8443"
& "$root\.venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8443 --ssl-keyfile "$root\certs\server.key" --ssl-certfile "$root\certs\server.crt" --ssl-ca-certs "$root\certs\ca.crt" --ssl-cert-reqs 2
