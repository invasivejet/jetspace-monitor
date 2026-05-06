#!/usr/bin/env bash
# Generate a dedicated Ed25519 key inside WSL (use when git runs in WSL).
# Usage: bash scripts/ssh-keygen-github-wsl.sh invasivejet
set -eu

TAG="${1:-invasivejet}"
KEY="$HOME/.ssh/id_ed25519_${TAG}"

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if [[ -e "$KEY" ]]; then
  echo "Key already exists: $KEY" >&2
  exit 1
fi

ssh-keygen -t ed25519 -C "GitHub ${TAG} ($(hostname))" -f "$KEY"

echo ""
echo "=== Add this PUBLIC key to GitHub (account: ${TAG}) → Settings → SSH keys ==="
cat "${KEY}.pub"
echo ""
echo "Then add Host github.com-ij (or similar) to ~/.ssh/config with:"
echo "  IdentityFile $KEY"
