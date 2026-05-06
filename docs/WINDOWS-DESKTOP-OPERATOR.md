# Lightweight Windows executable — your PC health + intelligent disk headroom

## What this is for

**Jetspace Monitor** is built to run **on your machine**, **localhost-only**, so you can:

- See **CPU / RAM / disk / pressure** and trends (`/control`, `/mini`, `WS /ws`).
- Run **gated cleanup** — temp/cache style paths, **dry-run by default**, **pressure gates** so cleanup does not hammer a hot system (`/cleanup/plan`, `/cleanup/run`).
- Optionally use **Modal** for **remote** CPU/GPU jobs (math/physics-style workloads) while **secrets and policy** stay local — see `GET /modal/workflow` and `docs/architecture.md`.

It is **not** a cloud dashboard for strangers; the point is **your** PC health and **safe** space recovery.

## Links to the source (verify pushes)

- **Primary (invasivejet):** https://github.com/invasivejet/jetspace-monitor  
- **Mirror / legacy:** https://github.com/joel-saucedo/jetspace-monitor  

Both should show the same `main` after you run dual pushes.

## Build the Windows bundle (PyInstaller `onedir`)

From **PowerShell** (repo root), with backend venv + Node for frontend build:

```powershell
cd C:\Users\joela\jetspace-monitor
.\scripts\build-jetspace-exe.ps1
```

Output:

```text
backend\dist\JetspaceMonitor\JetspaceMonitor.exe
```

**First run:** double-click `JetspaceMonitor.exe`. It:

1. `chdir` to the folder containing the exe (put `secrets\` / `data\` beside it if you use the encrypted bridge journal).
2. Starts **FastAPI** on **http://127.0.0.1:8010**
3. Opens **`/control`** in your default browser.

Faster iteration without packaging:

```powershell
cd backend
..\.venv\Scripts\python.exe jetspace_desktop.py
```

## Free space the “intelligent” way (safeguards)

1. Open **`http://127.0.0.1:8010/control`** → **Dry-run cleanup** (plan only).
2. Review gates in `backend/cleanup.py` / env in `backend/.env.example` (`JETSPACE_CLEANUP_*`, `JETSPACE_MIN_FREE_DISK_GB`, etc.).
3. Apply only when pressure is acceptable — weekly scripts already use gates (`scripts/maintenance-weekly.ps1`).

## Modal + safety (agents / tools / computation)

- **Local** = Cursor, PowerShell, this API, your schedulers.  
- **Modal** = optional **remote containers** for heavy steps; contract: **`GET /modal/workflow`** (tiers: `local_shell` vs `modal_remote_cpu` vs `modal_remote_gpu`).  
- **Do not** put API tokens in repo or chat; use `modal secret` and `modal setup`.

For math/physics-style compute, add or extend apps under `modal/` and keep **one** clear entry file per job type — see `modal/runtime_telemetry.py` as a pattern.

## Git from CLI (WSL) after SSH is fixed

```bash
cd /mnt/c/Users/joela/jetspace-monitor
git status
git add -A
git commit -m "Your message"
git push origin main              # invasivejet (use Host github.com-ij)
git push joel-saucedo main        # optional mirror
```

Verify SSH:

```bash
ssh -T git@github.com-ij
# Hi invasivejet! ...
```

## Reducing local heat

- Raise `JETSPACE_WS_INTERVAL_SEC`, `JETSPACE_MINIMON_INTERVAL_SEC` in `.env` (see `backend/.env.example`).
- Turn off schedulers you do not need (Task Scheduler: Jetspace minimon / maintenance).
