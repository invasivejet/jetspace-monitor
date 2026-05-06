#!/usr/bin/env bash
# Run from ANY directory under WSL:
#   bash /mnt/c/Users/<you>/jetspace-monitor/ssh-keygen-wsl.sh joel
# From Windows PowerShell (use Run-WslSshKeygen.ps1 instead of Git Bash for /mnt paths).
set -eu
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$HERE/scripts/ssh-keygen-github-wsl.sh" "$@"
