#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$ROOT/backend"
export JETSPACE_ROOT="$ROOT"

echo "[1/3] Ensure API is running on localhost:8010..."
if ! python3 - <<'PY'
import urllib.request
urllib.request.urlopen("http://127.0.0.1:8010/health", timeout=2)
print("api-ok")
PY
then
  echo "API not running; starting WSL-local API..."
  (
    cd "$BACKEND_DIR"
    nohup python3 -m uvicorn app:app --host 127.0.0.1 --port 8010 >/tmp/jetspace_api.log 2>&1 &
  )
  sleep 3
fi

echo "[2/3] Ensure PDF dependencies are available..."
python3 - <<'PY'
import importlib, subprocess, sys
for mod, pkg in [("reportlab", "reportlab"), ("fpdf", "fpdf2")]:
    try:
        importlib.import_module(mod)
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", pkg])
PY

echo "[3/3] Generate harmony audit report bundle..."
python3 "$BACKEND_DIR/scripts/harmony_audit.py"

echo "Report directory:"
echo "$ROOT/reports"
