#!/usr/bin/env bash
# Push current branch to both GitHub remotes (origin + mirror).
set -euo pipefail
branch="${1:-$(git rev-parse --abbrev-ref HEAD)}"
echo "Pushing ${branch} to origin..."
git push origin "${branch}"
echo "Pushing ${branch} to mirror..."
git push mirror "${branch}"
echo "Done."
