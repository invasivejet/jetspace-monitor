# Architecture

## Agent Loop

1. Observe: collect system metrics every second.
2. Model: compute first and second derivatives for CPU usage.
3. Decide: classify pressure events when thresholds are exceeded.
4. Act: log recommendations only (no process/file mutation).
5. Remember: keep rolling history for UI and future policy upgrades.

## API Endpoints

- `GET /health`
- `GET /stats`
- `GET /history?count=60`
- `WS /ws`

## Next Iterations

- Add GPU telemetry via `nvidia-smi` when available.
- Add policy module with adaptive thresholds.
- Add WSL metrics bridge.

## Cross-OS Secure Bridge

### Protocol

- Transport: HTTPS with mutual TLS (`/bridge/*`)
- Message auth: HMAC-SHA256 signature in `x-signature`
- Payload schema: `source`, `ts`, `state`, `d_state`, `anomaly_score`, `confidence`

### Runtime Components

- `bridge/models.py`: correlation payload contract
- `bridge/security.py`: signing + verification
- `bridge/policy.py`: rolling decision policy (`normal`, `watch`, `pressure`, `alert`)
- `bridge/journal.py`: encrypted append-only journal

### Resilience Path

1. Receive + verify message.
2. Evaluate policy and classify.
3. Append event to encrypted journal.
4. Serve recent events for replay and diagnostics.

## Safe Cleanup Subsystem

### Objectives

- Reduce storage pressure without risking system integrity.
- Reclaim space with predictable bounds and auditability.

### Components

- `cleanup.py`: safe cleaner with policy-based constraints
- `scripts/cleanup_once.py`: one-shot dry-run/apply runner
- `/cleanup/*` endpoints: plan, execute, and inspect cleanup history

### Reliability Controls

- Dry-run default (`JETSPACE_CLEANUP_DRY_RUN=true`)
- Age gate (`JETSPACE_CLEANUP_MIN_AGE_HOURS`, default 24h)
- Deletion budget per run (`JETSPACE_CLEANUP_MAX_DELETE_MB`)
- Max item cap (`JETSPACE_CLEANUP_MAX_ITEMS`)
- Explicit apply confirmation (`confirm=true`)
- Overload gate (`JETSPACE_CLEANUP_MAX_CPU_PERCENT`, `JETSPACE_CLEANUP_MAX_RAM_PERCENT`)
- Free-disk floor gate (`JETSPACE_CLEANUP_MIN_FREE_DISK_GB`)

## Physics-Coded Operations

### State Variables

- `x = (cpu, ram, disk)` resource coordinates
- `dx/dt = (d_cpu, d_ram)` first derivative flow
- `d2cpu/dt2` acceleration surrogate for volatility
- `pressure` scalar for intervention readiness

### Operational Policy

- Daily: plan-only simulation for deterministic reclaim estimates.
- Weekly: bounded apply; auto-downgrades to dry-run when pressure is unsafe.
- Each run persists structured audit output for replay and diagnostics.

## Modal: cross-OS execution semantics

Jetspace treats Modal as **remote container compute** (Modal’s fleet), separate from **local** Cursor, PowerShell, bash, and the **localhost FastAPI** control plane.

### Canonical environment

- `JETSPACE_ROOT`: repo root (optional; otherwise inferred from `backend/jetspace_paths.py`).
- `JETSPACE_REPORTS_DIR`: where JSON/MD/PDF diagnostics land (default `<root>/reports`).
- `JETSPACE_API_BASE`: local physics/control API (default `http://127.0.0.1:8010`).

### Operation tiers (semantic labels)


| Tier               | Where it runs             | Typical operations                                                         |
| ------------------ | ------------------------- | -------------------------------------------------------------------------- |
| `local_shell`      | Windows or Linux **host** | `modal` CLI, `modal_network_diagnose.py`, `harmony_audit.py`, git, scripts |
| `local_fastapi`    | Host loopback             | `/physics/state`, `/cleanup/`*, `/bridge/`*, `/modal/workflow`             |
| `modal_remote_cpu` | Modal **CPU** container   | `modal/get_started.py`, `modal/secret_probe.py`, `remote_cpu_telemetry`    |
| `modal_remote_gpu` | Modal **GPU** container   | `remote_gpu_telemetry` (`nvidia-smi` on worker; may skip if no GPU)        |


### Agent rule of thumb (Cursor on Windows vs Linux)

1. Read the contract: `GET /modal/workflow` on the local API (or open `backend/modal_workflow.py`).
2. **Never** conflate “Modal CLI works” with “GPU job ran”: CLI probes are `local_shell`; GPU evidence requires `modal_remote_gpu` results.
3. Keep one **canonical checkout path**; WSL uses the same tree via `/mnt/<drive>/...` when applicable.
4. Secrets: only via `modal secret` / Modal dashboard — not repo, not chat.

### Entrypoints

- Windows: `scripts/modal-setup.ps1`, `scripts/modal-network-diagnose.ps1`
- WSL/Linux: `scripts/wsl-modal-setup.sh`, `scripts/wsl-modal-network-diagnose.sh`
- Remote telemetry: `modal run modal/runtime_telemetry.py` (from repo root)

## Publishing: same repo on two GitHub accounts

To keep **one codebase** reachable from both a personal account (e.g. `joel-saucedo`) and another namespace (e.g. `invasivejet`), use **two Git remotes** and push the same branches to both. Keep **LICENSE and contributor attribution** accurate; do not use Git mechanics to misrepresent ownership.

Step-by-step commands and SSH multi-account notes: **`AGENTS.md`** (section “GitHub: two namespaces”).