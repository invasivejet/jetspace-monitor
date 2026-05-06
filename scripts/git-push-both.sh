#!/usr/bin/env bash
# Push current branch to primary + secondary remotes.
# Canonical: origin (invasivejet), then joel-saucedo if present, else mirror.
set -euo pipefail
branch="${1:-$(git rev-parse --abbrev-ref HEAD)}"
echo "Pushing ${branch} to origin..."
git push origin "${branch}"
if git remote get-url joel-saucedo >/dev/null 2>&1; then
  echo "Pushing ${branch} to joel-saucedo..."
  git push joel-saucedo "${branch}"
elif git remote get-url mirror >/dev/null 2>&1; then
  echo "Pushing ${branch} to mirror..."
  git push mirror "${branch}"
else
  echo "No secondary remote (joel-saucedo or mirror). Only origin was pushed."
fi
echo "Done."
