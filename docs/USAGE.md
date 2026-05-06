# Jetspace Monitor — what it is and how to use it

## What it does

**Jetspace Monitor** is a **localhost-first** control and observability stack:

1. **FastAPI backend** (`backend/`) — exposes system metrics, a **physics-style pressure model** (CPU/RAM/disk, derivatives, bounded `pressure`), **safe cleanup** planning/apply with overload gates, optional **signed bridge** events, and **Modal workflow** metadata (`GET /modal/workflow`).
2. **React dashboard** (`frontend/`) — real-time charts via WebSocket (`WS /ws`), aligned with API on **port 8010** by default.
3. **Scripts** (`scripts/`) — Windows/WSL maintenance, security checkpoints, Modal setup/diagnostics, Git helpers for **invasivejet** as canonical `origin`.
4. **Modal apps** (`modal/`) — optional remote CPU/GPU telemetry and examples (secrets via Modal only).

Nothing in the default design **exposes the control API to the public internet**; bind stays on **127.0.0.1** in production-style launchers.

## Who it is for

- Operators who want a **small, auditable** panel (`/control`, `/mini`) and JSON reports under `reports/` (gitignored locally).
- Developers using **Cursor** or other agents: see **`AGENTS.md`** and **`.cursor/rules/jetspace-compute.mdc`**.

## Quick start (Windows)

```powershell
cd C:\Users\<you>\jetspace-monitor
.\scripts\dev.ps1 -Install
```

- API: `http://127.0.0.1:8010` — `GET /health`, `GET /physics/state`, `GET /modal/workflow`
- UI dev server: `http://127.0.0.1:5173`
- Compact panel: `http://127.0.0.1:8010/control`

## Quick start (backend only)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8010
```

## Desktop `.exe` (Windows)

```powershell
cd C:\Users\<you>\jetspace-monitor
.\scripts\build-jetspace-exe.ps1
```

Run `backend\dist\JetspaceMonitor\JetspaceMonitor.exe` — starts the API and opens **`/control`**.

## Environment variables (optional)

See **`backend/.env.example`**: `JETSPACE_*`, bridge secret, telemetry intervals (`JETSPACE_WS_INTERVAL_SEC`, etc.).

## Git: canonical remote (**invasivejet**, private repo)

This project is intended to live at **`invasivejet/jetspace-monitor`** (private on GitHub). On GitHub: create an empty **private** repo with that name, then:

```powershell
cd C:\Users\<you>\jetspace-monitor
.\scripts\set-origin-invasivejet.ps1
.\scripts\verify-git-flow.ps1
git push -u origin main
```

If SSH uses a host alias (e.g. `github.com-ij`), pass `-SshHostAlias github.com-ij` to `set-origin-invasivejet.ps1`.

The previous **`joel-saucedo`** remote is kept as **`joel-saucedo`** for fetch/merge when needed. Full notes: **`docs/GITHUB-REMOTES-AND-ORGS.md`**.

### If `git push` says “Permission denied … to joel-saucedo”

Your SSH client is offering **joel-saucedo’s** key to `git@github.com`, but **`origin`** points at **invasivejet**’s repo. GitHub rejects that.

**Fix (pick one):**

1. **SSH config host alias** (recommended): add a `Host` block for **invasivejet**’s key (see `scripts/ssh-config.github.template`), then set:

   ```bash
   git remote set-url origin git@github.com-ij:invasivejet/jetspace-monitor.git
   ```

   (`github.com-ij` must match your `~/.ssh/config` `Host` name.)

2. **Test:** `ssh -T git@github.com-ij` should print **invasivejet**, not joel-saucedo.

3. **Then:** `git push -u origin main`

## Further reading

| Doc | Topic |
|-----|--------|
| `docs/architecture.md` | Design, bridge, cleanup, Modal tiers |
| `docs/PACKAGING.md` | What belongs in Git vs local-only |
| `docs/GITHUB-REMOTES-AND-ORGS.md` | invasivejet, jetbundle org, remotes |
| `docs/PRIVATE-REPO-FIRST-PUSH.md` | Private repo on invasivejet + first `git push` |
| `docs/ROADMAP-SITE-AND-COMPUTE.md` | jetbundle.github.io vs hosted API |
| `README.md` | Extended quick start, Modal, hotkeys |

### Commit + push (script finds `git.exe`)

```powershell
cd C:\Users\<you>\jetspace-monitor
.\scripts\commit-and-push-origin.ps1 -Message "Describe your change"
```
