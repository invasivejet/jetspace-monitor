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

## GitHub: two namespaces (e.g. personal + `invasivejet`)

Use **two remotes** and normal Git history — keep **LICENSE and contributors** accurate.

```text
origin     → primary repo you work against daily (e.g. joel-saucedo/jetspace-monitor)
mirror     → second GitHub repo (e.g. invasivejet/jetspace-monitor)
```

Add the second remote once the empty repo exists on GitHub:

```bash
git remote add mirror https://github.com/invasivejet/jetspace-monitor.git
# or SSH: git@github.com:invasivejet/jetspace-monitor.git
git fetch mirror
git push mirror main
```

Ongoing:

```bash
git push origin main
git push mirror main
```

For **SSH with two GitHub accounts**, use separate keys and `~/.ssh/config` `Host` aliases. Point **`origin`** at the host alias for `joel-saucedo` and **`mirror`** at the alias for `invasivejet` so each `git push` uses the correct key.

### Example `~/.ssh/config` (WSL or Windows OpenSSH)

Use your real key paths. `IdentitiesOnly yes` avoids the wrong key being offered first.

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

Then set remotes (after repos exist on GitHub):

```bash
git remote add origin git@github.com-js:joel-saucedo/jetspace-monitor.git
# or: gh repo create ... sets HTTPS origin; switch with git remote set-url
./scripts/setup-github-mirror-remote.sh github.com-ij invasivejet jetspace-monitor
```

**Push both** in one step:

- WSL / Git Bash: `bash scripts/git-push-both.sh`
- PowerShell: `.\scripts\git-push-both.ps1`

**Day-to-day “toggle”:** you do not switch GitHub accounts in Git itself — you only choose *which remote* you push to (`origin`, `mirror`, or both). Keep `user.name` / `user.email` consistent with the identity that should own the commits (usually one primary author; see README / LICENSE).

### First-time checklist for `invasivejet`

1. On GitHub, log in as **invasivejet** → create an empty **private** repo `jetspace-monitor` (no README).
2. Generate an SSH key and add the **public** key to **invasivejet** → Settings → SSH keys.
3. In this clone, run `setup-github-mirror-remote` with your chosen SSH host alias.
4. `git push mirror main` (or `git-push-both`).

This “couples” the same codebase to both accounts **transparently in Git** (two URLs), not by hiding who maintains what.