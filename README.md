# Jetspace Monitor

Organized MVP for safe, real-time system observability.

**User guide (what it does, how to run it, private GitHub on invasivejet):** [`docs/USAGE.md`](docs/USAGE.md) · **First private push:** [`docs/PRIVATE-REPO-FIRST-PUSH.md`](docs/PRIVATE-REPO-FIRST-PUSH.md) · **Site → compute roadmap:** [`docs/ROADMAP-SITE-AND-COMPUTE.md`](docs/ROADMAP-SITE-AND-COMPUTE.md)

## Structure

- `backend/` FastAPI + WebSocket system metrics service
- `frontend/` React + Vite dashboard
- `docs/` architecture, packaging, and operating notes

**Publishing / what belongs on GitHub:** see [`docs/PACKAGING.md`](docs/PACKAGING.md) (invariants, ignored paths, WSL vs PowerShell paths).

**Git remotes (invasivejet = canonical `origin`), jetbundle org, Pages repo notes:** [`docs/GITHUB-REMOTES-AND-ORGS.md`](docs/GITHUB-REMOTES-AND-ORGS.md).  
Verify wiring: `.\scripts\verify-git-flow.ps1`

**Windows desktop `.exe` (PC health + safe cleanup + Modal notes):** [`docs/WINDOWS-DESKTOP-OPERATOR.md`](docs/WINDOWS-DESKTOP-OPERATOR.md) — build: `.\scripts\build-jetspace-exe.ps1` → `backend\dist\JetspaceMonitor\JetspaceMonitor.exe`.

## Quick Start (Windows PowerShell)

### 0) One command launcher

```powershell
.\scripts\dev.ps1 -Install
```

This starts backend + frontend in separate PowerShell windows.

### 1) Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8010
```

### 2) Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173/index.html`.

## Safety

- Dashboard is observe/recommend only.
- No destructive automation.
- API bound to localhost in dev.

## Secure Windows-WSL Bridge (mTLS + Signed Payloads)

1. Set shared secret:

```powershell
$env:JETSPACE_BRIDGE_SHARED_SECRET = "change-this-shared-secret"
```

1. Start secure bridge server:

```powershell
cd backend
.\scripts\start_bridge.ps1
```

1. Send a signed sample correlation from client:

```powershell
cd backend
$env:JETSPACE_BRIDGE_SHARED_SECRET = "change-this-shared-secret"
.\.venv\Scripts\python scripts\send_wsl_sample.py
```

1. Validate received events:

```powershell
python -c "import ssl, urllib.request; ctx=ssl.create_default_context(cafile='backend/certs/ca.crt'); ctx.load_cert_chain(certfile='backend/certs/client.crt', keyfile='backend/certs/client.key'); print(urllib.request.urlopen('https://127.0.0.1:8443/bridge/events?count=5', context=ctx).read().decode())"
```

### Security Properties

- mTLS enforces mutual certificate trust.
- HMAC signature (`x-signature`) protects payload integrity.
- Encrypted journal (`backend/data/bridge-journal.log`) supports replay/resilience.

## Safe Cleanup Automation (Memory/Storage Efficiency)

This cleaner only targets cache/temp paths and is dry-run by default.

### Dry-run cleanup

```powershell
.\scripts\safe-clean.ps1
```

### Apply cleanup (explicit)

```powershell
cd backend
$env:JETSPACE_CLEANUP_DRY_RUN="false"
.\.venv\Scripts\python scripts\cleanup_once.py --apply
```

### API controls

- `GET /cleanup/plan` -> dry-run plan and estimated reclaimed bytes
- `POST /cleanup/run?confirm=true&dry_run=true` -> safe simulation
- `POST /cleanup/run?confirm=true&dry_run=false` -> apply cleanup
- `GET /cleanup/history` -> recent cleanup runs

### Guardrails

- Protected path allow/block logic (no system roots)
- Minimum item age threshold
- Maximum delete budget per run
- Large-item-first strategy for best reclaim efficiency
- Cleanup run audit artifacts in `backend/data/cleanup-last.json`

## Physics-Coded Reliability Layer

- `GET /physics/state` exposes dynamic state manifold:
  - `cpu`, `ram`, `disk`
  - first derivatives `d_cpu`, `d_ram`
  - curvature proxy `d2_cpu`
  - bounded pressure scalar `pressure in [0,1]`
  - free resource reserves (`free_mem_gb`, `free_disk_gb`)
- Cleanup writes an autoencoded artifact:
  - `backend/data/cleanup-last.autoencoded` (gzip + base64)

## Professional Maintenance Scheduling

Install scheduled tasks:

```powershell
.\scripts\install-maintenance-schedule.ps1
```

Runs created:

- `Jetspace-Maintenance-Daily-Plan` (03:10 daily, dry-run planning)
- `Jetspace-Maintenance-Weekly-Apply` (03:30 Sunday, bounded apply with pressure gates)

## Compact Always-On Monitor (Airgapped-Style)

Design goals:

- localhost-only telemetry surface (no remote egress behavior)
- low-overhead loop (interval configurable; see `JETSPACE_MINIMON_INTERVAL_SEC` in `backend/.env.example`)
- bounded append-only local stream for diagnostics
- ethical scope: observe/diagnose, never covertly exfiltrate/control

### Run now

```powershell
cd backend
.\.venv\Scripts\python scripts\minimon_agent.py
```

### Compact UI

- Start API: `cd backend; .\.venv\Scripts\python -m uvicorn app:app --host 127.0.0.1 --port 8010`
- Open: `http://127.0.0.1:8010/mini`

### Startup automation

- Task-scheduler installer: `.\scripts\install-minimon-schedule.ps1`
- If task creation is blocked by OS policy, fallback launcher is created at:
  - `C:\Users\joela\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\jetspace-minimon-startup.cmd`

## Modal Quickstart (WSL)

Important:

- Never paste API secrets into chat or code files.
- Use `python3 -m modal setup` (browser auth) instead of fake placeholders like `NEW_ID`.

Run:

```bash
cd /path/to/jetspace-monitor
bash scripts/wsl-modal-setup.sh
```

### Modal Quickstart (Windows / native Cursor)

From the repo root:

```powershell
.\scripts\modal-setup.ps1
```

Diagnostics only (no Modal install):

```powershell
.\scripts\modal-network-diagnose.ps1
```

**Cross-machine agents:** the semantic contract (what runs locally vs on Modal CPU vs GPU) is served at `GET http://127.0.0.1:8010/modal/workflow` when the API is up, or read `backend/modal_workflow.py`.

Optional: set `JETSPACE_ROOT` / `JETSPACE_REPORTS_DIR` so audits and Modal diagnose JSON always land in the same folder on every clone.

Included examples:

- `modal/get_started.py` (remote square function)
- `modal/secret_probe.py` (`custom-secret` with key `jetspace`, safe metadata only)
- `modal/runtime_telemetry.py` (explicit **CPU** vs **GPU** worker telemetry; no secrets)

## Native Hotkey Control Runtime

- Runtime launcher: `scripts/launch-control-runtime.cmd`
- Startup autoload: `C:\Users\joela\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\jetspace-control-runtime.cmd`
- Global shortcut: `Ctrl+Alt+J` opens `http://127.0.0.1:8010/control`

Windows security note:

- `Ctrl+Alt+Delete` is a protected secure-attention sequence and cannot be replaced by third-party/local apps.
- This setup provides the closest responsible native workflow: secure sequence remains untouched, and panel access is immediate via global hotkey.

