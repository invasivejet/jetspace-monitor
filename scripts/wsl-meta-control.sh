#!/usr/bin/env bash
set -euo pipefail

# Single-command launcher from WSL Ubuntu.
# Starts Windows-hosted API and opens purple terminal meta monitor.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_WSL="$ROOT/backend"
export JETSPACE_ROOT="$ROOT"
HOST_IP="$(grep -m1 nameserver /etc/resolv.conf | awk '{print $2}')"
API_LOCAL="http://127.0.0.1:8010"
API_HOST="http://${HOST_IP}:8010"
API_BASE="$API_LOCAL"
export API_BASE

echo "[1/3] Starting local control API in WSL (localhost:8010)..."
if ! python3 - <<PY
import urllib.request
try:
    urllib.request.urlopen("${API_LOCAL}/health", timeout=1)
except Exception:
    raise SystemExit(1)
PY
then
  (
    cd "$BACKEND_WSL"
    if ! python3 - <<'PY'
import fastapi, uvicorn, psutil, cryptography  # noqa: F401
print("deps-ok")
PY
    then
      python3 -m pip install --user --upgrade pip >/tmp/jetspace_api_start.log 2>&1
      python3 -m pip install --user -r requirements.txt >>/tmp/jetspace_api_start.log 2>&1
    fi
    nohup python3 -m uvicorn app:app --host 127.0.0.1 --port 8010 >/tmp/jetspace_api.log 2>&1 &
  )
fi

for i in $(seq 1 40); do
  if python3 - <<PY
import urllib.request
try:
    urllib.request.urlopen("${API_LOCAL}/health", timeout=1)
    print("ok")
except Exception:
    raise SystemExit(1)
PY
  then
    API_BASE="$API_LOCAL"
    break
  fi
  if python3 - <<PY
import urllib.request
try:
    urllib.request.urlopen("${API_HOST}/health", timeout=1)
    print("ok")
except Exception:
    raise SystemExit(1)
PY
  then
    API_BASE="$API_HOST"
    break
  fi
  sleep 1
done

if ! python3 - <<PY
import urllib.request
urllib.request.urlopen("${API_BASE}/health", timeout=2)
PY
then
  echo "API did not become reachable from WSL."
  if [ -f /tmp/jetspace_api.log ]; then
    echo "--- /tmp/jetspace_api.log (tail) ---"
    tail -n 40 /tmp/jetspace_api.log || true
  fi
  exit 1
fi

echo "[2/3] Running safe purge dry-run via API..."
python3 - <<'PY'
import json, urllib.request
import os
u = os.environ["API_BASE"] + "/cleanup/run?confirm=true&dry_run=true"
req = urllib.request.Request(u, method="POST")
with urllib.request.urlopen(req, timeout=20) as r:
    d = json.loads(r.read().decode())
print(f"dry_run={d.get('dry_run')} planned={d.get('planned_items')} reclaim_mb={d.get('reclaimed_bytes',0)/(1024*1024):.1f} skipped_load={d.get('skipped_due_to_load')}")
PY

echo "[3/3] Launching meta terminal (Ctrl+C to quit)..."
JETSPACE_API_BASE="$API_BASE" python3 "$BACKEND_WSL/scripts/meta_tui.py"
