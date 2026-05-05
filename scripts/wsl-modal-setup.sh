#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export JETSPACE_ROOT="$ROOT"

echo "[1/6] Installing Modal client in user environment..."
python3 -m pip install --user --upgrade modal

echo "[2/6] Starting browser-based Modal authentication..."
echo "Complete login in browser, then return here."
python3 -m modal setup

echo "[3/6] Checking active profile..."
modal profile current

echo "[4/6] Creating/updating custom-secret with key 'jetspace'..."
read -r -s -p "Enter secret value for custom-secret[jetspace]: " JETSPACE_VALUE
echo
modal secret create custom-secret jetspace="$JETSPACE_VALUE" --force
unset JETSPACE_VALUE

echo "[5/6] Running Modal examples (CPU workers)..."
modal run "$ROOT/modal/get_started.py"
modal run "$ROOT/modal/secret_probe.py"

echo "[6/6] Optional runtime telemetry (CPU + GPU worker if available)..."
set +e
modal run "$ROOT/modal/runtime_telemetry.py"
set -e

echo "Done. Modal setup + secret wiring verified."
