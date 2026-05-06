# Agent brief — Jetspace Monitor

Hand this file (and `.cursor/rules/jetspace-compute.mdc`) to any automated agent or collaborator.

## Permanent path pattern

There is no single global path; each machine has its own clone. Standardize with:


| OS      | Typical layout                                                    |
| ------- | ----------------------------------------------------------------- |
| Windows | `C:\Users\<account>\jetspace-monitor`                             |
| WSL     | `/mnt/c/Users/<account>/jetspace-monitor` (same files as Windows) |
| Linux   | `~/projects/jetspace-monitor` (or your chosen path)               |


Set `JETSPACE_ROOT` to the repo root when paths must match across tools.

## Environment

- `JETSPACE_ROOT`, `JETSPACE_REPORTS_DIR`, `JETSPACE_API_BASE` — see `backend/.env.example`
- Bridge signing: `JETSPACE_BRIDGE_SHARED_SECRET` (never commit real values)

## API contract

With the FastAPI app on **127.0.0.1:8010** (see `scripts/dev.ps1`, `scripts/secure-harmonize.ps1`, `scripts/launch-control-runtime.cmd`):

1. `GET /modal/workflow` — **Modal vs local execution semantics**
2. `GET /physics/state` — pressure, derivatives, free mem/disk
3. `WS /ws` — realtime telemetry for dashboards
4. `GET /interop/summary` — cross-OS file/localhost notes

Full architecture: `docs/architecture.md`

## Modal

- Contract and tiers: `backend/modal_workflow.py` and `GET /modal/workflow`
- Do not store Modal tokens in the repo; use `modal setup` and Modal Secrets.

## GitHub: canonical **invasivejet** + legacy **joel-saucedo**

Full detail: **`docs/GITHUB-REMOTES-AND-ORGS.md`**, first private push: **`docs/PRIVATE-REPO-FIRST-PUSH.md`**.

**Canonical layout** (what `verify-git-flow.ps1` expects):

```text
origin       → invasivejet/jetspace-monitor   (day-to-day pull / push)
joel-saucedo → joel-saucedo/jetspace-monitor  (optional; saved when you run set-origin-invasivejet.ps1)
```

Use **`.\scripts\set-origin-invasivejet.ps1`** from repo root so `origin` uses SSH host **`github.com-ij`** and the previous `origin` is preserved as **`joel-saucedo`**.

For **two keys**, add `Host github.com-js` and `Host github.com-ij` in `~/.ssh/config` (template: `scripts/ssh-config.github.template`). Example:

```sshconfig
Host github.com-js
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_joel
  IdentitiesOnly yes

Host github.com-ij
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_invasivejet
  IdentitiesOnly yes
```

Then `origin` should look like: `git@github.com-ij:invasivejet/jetspace-monitor.git`.

**Push both copies** (origin + joel-saucedo, or origin + mirror if you use that name):

- PowerShell: `.\scripts\git-push-both.ps1` (uses `Find-Git.ps1` if `git` is not on PATH)
- WSL: `bash scripts/git-push-both.sh`

**Optional** extra remote named `mirror` (any owner/repo): `.\scripts\setup-github-mirror-remote.ps1` or  
`bash scripts/setup-github-mirror-remote.sh github.com-ij invasivejet jetspace-monitor mirror`

Automation (Cursor cloud agents, some CI) often **cannot** run `git push` with your SSH keys — run push/verify on your PC.

This “couples” the same codebase to two GitHub namespaces **via two remote URLs**, not by hiding attribution. Keep **`user.name` / `user.email`** honest (see README / LICENSE).