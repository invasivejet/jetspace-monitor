#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BRANCH="${1:-$(git rev-parse --abbrev-ref HEAD)}"
echo "Pushing branch: $BRANCH"

git remote get-url origin >/dev/null
git remote get-url mirror >/dev/null

git push -u origin "$BRANCH"
git push -u mirror "$BRANCH"
