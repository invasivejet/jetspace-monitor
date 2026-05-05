#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export JETSPACE_ROOT="$ROOT"

echo "[1/2] Running Modal network diagnostics..."
python3 "$ROOT/backend/scripts/modal_network_diagnose.py"

echo "[2/2] Done. Report directory:"
echo "$ROOT/reports"
