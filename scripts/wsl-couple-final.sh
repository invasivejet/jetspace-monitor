#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export JETSPACE_ROOT="$ROOT"
WIN_PS="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
WIN_PWSH="/mnt/c/Program Files/PowerShell/7/pwsh.exe"

run_windows_ps() {
  local script_win="$1"
  if [ -x "$WIN_PS" ]; then
    "$WIN_PS" -NoProfile -ExecutionPolicy Bypass -File "$script_win"
    return 0
  fi
  if [ -x "$WIN_PWSH" ]; then
    "$WIN_PWSH" -NoProfile -ExecutionPolicy Bypass -File "$script_win"
    return 0
  fi
  return 1
}

echo "[1/5] Run security checkpoints on Windows..."
SEC_SCRIPT_WIN=""
if command -v wslpath >/dev/null 2>&1; then
  SEC_SCRIPT_WIN="$(wslpath -w "$ROOT/scripts/security-checkpoints.ps1" 2>/dev/null || true)"
fi
if [ -n "$SEC_SCRIPT_WIN" ]; then
  if ! run_windows_ps "$SEC_SCRIPT_WIN" >/dev/null 2>&1; then
    echo "security-checkpoints.ps1 did not complete (PowerShell missing or script error)."
  fi
else
  echo "wslpath unavailable; skipping Windows security-checkpoints from WSL."
fi

echo "[2/5] Run harmony physics audit..."
bash "$ROOT/scripts/wsl-harmony-audit.sh"

echo "[3/5] Run Modal connectivity diagnostics..."
bash "$ROOT/scripts/wsl-modal-network-diagnose.sh"

echo "[4/5] Launch dark-purple meta monitor..."
nohup bash "$ROOT/scripts/wsl-meta-control.sh" >/tmp/jetspace_meta_run.log 2>&1 &
sleep 2

echo "[5/5] Final coupling status..."
python3 - <<PY
import os, pathlib
root = pathlib.Path(os.environ.get("JETSPACE_ROOT", ".")).resolve()
reports = root / "reports"
latest = sorted(reports.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
print("Recent report files:")
for p in latest:
    print(" -", p.name)
print("Coupling complete. Reports directory:")
print(reports)
PY
