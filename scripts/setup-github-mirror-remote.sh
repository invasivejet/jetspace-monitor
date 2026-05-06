#!/usr/bin/env bash
# Add or update a second remote (default name: mirror) for another GitHub namespace.
# Usage: bash scripts/setup-github-mirror-remote.sh [ssh-host-alias] [owner] [repo] [remote-name]
# Example: bash scripts/setup-github-mirror-remote.sh github.com-ij joel-saucedo jetspace-monitor joel-saucedo
set -euo pipefail
SSH_HOST_ALIAS="${1:-github.com-ij}"
OWNER="${2:-invasivejet}"
REPO="${3:-jetspace-monitor}"
REMOTE_NAME="${4:-mirror}"
URL="git@${SSH_HOST_ALIAS}:${OWNER}/${REPO}.git"
if git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
  git remote set-url "${REMOTE_NAME}" "$URL"
  echo "Updated ${REMOTE_NAME} -> $URL"
else
  git remote add "${REMOTE_NAME}" "$URL"
  echo "Added ${REMOTE_NAME} -> $URL"
fi
git remote -v
