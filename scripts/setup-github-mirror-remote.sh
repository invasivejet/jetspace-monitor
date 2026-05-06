#!/usr/bin/env bash
set -euo pipefail

# Usage: bash scripts/setup-github-mirror-remote.sh [ssh-host-alias] [owner] [repo] [remote-name]
# Example: bash scripts/setup-github-mirror-remote.sh github.com-ij invasivejet jetspace-monitor mirror

ALIAS="${1:-github.com-ij}"
OWNER="${2:-invasivejet}"
REPO_NAME="${3:-jetspace-monitor}"
REMOTE="${4:-mirror}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

URL="git@${ALIAS}:${OWNER}/${REPO_NAME}.git"

if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "Updating remote '$REMOTE' -> $URL"
  git remote set-url "$REMOTE" "$URL"
else
  echo "Adding remote '$REMOTE' -> $URL"
  git remote add "$REMOTE" "$URL"
fi

echo ""
git remote -v
