#!/usr/bin/env bash
# Run in WSL after you add an Ed25519 key to the *invasivejet* GitHub account.
# Usage: bash scripts/wsl-fix-origin-invasivjet-ssh.sh
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
KEY="${HOME}/.ssh/id_ed25519_invasivejet"

if [[ ! -f "$KEY" ]]; then
  echo "Missing key: $KEY"
  echo "Generate: bash $ROOT/scripts/ssh-keygen-github-wsl.sh invasivejet"
  echo "Then add the printed .pub to GitHub (signed in as invasivejet) → SSH keys."
  exit 1
fi

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
touch "$HOME/.ssh/config"
chmod 600 "$HOME/.ssh/config"

if grep -q "Host github.com-ij" "$HOME/.ssh/config" 2>/dev/null; then
  echo "Host github.com-ij already in ~/.ssh/config — check IdentityFile points to:"
  echo "  $KEY"
else
  cat >> "$HOME/.ssh/config" <<EOF

Host github.com-ij
  HostName github.com
  User git
  IdentityFile $KEY
  IdentitiesOnly yes
EOF
  echo "Appended Host github.com-ij to ~/.ssh/config"
fi

cd "$ROOT"
git remote set-url origin "git@github.com-ij:invasivejet/jetspace-monitor.git"
echo ""
echo "Remotes:"
git remote -v
echo ""
echo "Next:"
echo "  ssh -T git@github.com-ij    # must say 'Hi invasivejet!'"
echo "  git push origin main"
