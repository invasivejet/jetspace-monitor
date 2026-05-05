#!/usr/bin/env bash
# Add or update the "mirror" remote for a second GitHub account (e.g. invasivejet).
set -euo pipefail
SSH_HOST_ALIAS="${1:-github.com-ij}"
OWNER="${2:-invasivejet}"
REPO="${3:-jetspace-monitor}"
URL="git@${SSH_HOST_ALIAS}:${OWNER}/${REPO}.git"
if git remote get-url mirror >/dev/null 2>&1; then
  git remote set-url mirror "$URL"
  echo "Updated mirror -> $URL"
else
  git remote add mirror "$URL"
  echo "Added mirror -> $URL"
fi
git remote -v
