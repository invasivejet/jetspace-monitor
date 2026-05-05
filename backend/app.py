import asyncio
import json
import platform
import time
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Deque, Dict, List

import psutil
from fastapi import FastAPI, Header, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from bridge.journal import EncryptedJournal
from bridge.models import CorrelationPayload
from bridge.policy import CorrelationPolicy
from bridge.security import get_bridge_secret, verify_payload_signature
from cleanup import SafeCleaner
from dynamics import PhysicsModel
from primitive import primitive_language, primitive_state, solved_minimal_problems
from modal_workflow import workflow_manifest


@dataclass
class Sample:
    ts: float
    cpu: float
    ram: float
    disk: float
    net_sent: float
    net_recv: float
    d_cpu: float
    d2_cpu: float


class MonitorState:
    def __init__(self, max_points: int = 300) -> None:
        self.points: Deque[Sample] = deque(maxlen=max_points)
        self.disk_root = "C:\\" if Path("C:\\").exists() else "/"
        self.prev_cpu: float | None = None
        self.prev_d_cpu: float | None = None
        self.prev_net_sent: float | None = None
        self.prev_net_recv: float | None = None

    def capture(self) -> Sample:
        ts = time.time()
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage(self.disk_root).percent

        net = psutil.net_io_counters()
        net_sent = float(net.bytes_sent)
        net_recv = float(net.bytes_recv)

        d_cpu = 0.0 if self.prev_cpu is None else cpu - self.prev_cpu
        d2_cpu = 0.0 if self.prev_d_cpu is None else d_cpu - self.prev_d_cpu

        sample = Sample(
            ts=ts,
            cpu=cpu,
            ram=ram,
            disk=disk,
            net_sent=0.0 if self.prev_net_sent is None else net_sent - self.prev_net_sent,
            net_recv=0.0 if self.prev_net_recv is None else net_recv - self.prev_net_recv,
            d_cpu=d_cpu,
            d2_cpu=d2_cpu,
        )

        self.prev_cpu = cpu
        self.prev_d_cpu = d_cpu
        self.prev_net_sent = net_sent
        self.prev_net_recv = net_recv
        self.points.append(sample)
        return sample

    def latest(self) -> Dict:
        if not self.points:
            return asdict(self.capture())
        return asdict(self.points[-1])

    def recent(self, count: int = 60) -> List[Dict]:
        return [asdict(x) for x in list(self.points)[-count:]]


app = FastAPI(title="Jetspace Monitor API", version="0.1.0")
state = MonitorState()
bridge_events: Deque[Dict] = deque(maxlen=500)
policy = CorrelationPolicy()
journal = EncryptedJournal(
    key_path=Path("secrets") / "journal.key",
    log_path=Path("data") / "bridge-journal.log",
)
cleaner = SafeCleaner()
cleanup_runs: Deque[Dict] = deque(maxlen=100)
physics = PhysicsModel()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/stats")
def stats() -> Dict:
    return state.latest()


@app.get("/history")
def history(count: int = 60) -> List[Dict]:
    return state.recent(count)


@app.websocket("/ws")
async def ws_stats(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            sample = state.capture()
            phys = physics.capture()
            await ws.send_json({"sample": asdict(sample), "physics": phys})
            await asyncio.sleep(1)
    except Exception:
        await ws.close()


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _reports_dir() -> Path:
    return _project_root() / "reports"


@app.get("/interop/summary")
def interop_summary() -> Dict:
    root = _project_root()
    reports = _reports_dir()
    return {
        "host_os": platform.system(),
        "host_release": platform.release(),
        "project_root": str(root),
        "reports_dir": str(reports),
        "wsl_path_hint": (
            "/mnt/c/.../jetspace-monitor — WSL can read/write the same working tree via /mnt/c, "
            "but WSL `localhost` is not Windows `localhost` unless you tunnel or mirror services."
        ),
        "recommended_patterns": [
            "Keep one canonical repo directory on Windows (ex: C:\\Users\\you\\jetspace-monitor) and use /mnt/c/Users/you/jetspace-monitor in WSL.",
            "Prefer the Windows API at http://127.0.0.1:8010 for operator UI/hotkeys; run WSL diagnostics that write JSON into reports/ for the same folder.",
            "For cross-OS HTTP, bind services to 127.0.0.1 on each side, or explicitly use the Windows host IP from WSL when you intentionally bridge.",
            "Modal semantics (local vs remote CPU/GPU): GET /modal/workflow on this API.",
        ],
    }


@app.get("/modal/latest-diagnostic")
def modal_latest_diagnostic() -> Dict:
    reports = _reports_dir()
    if not reports.exists():
        raise HTTPException(status_code=404, detail="reports directory missing")

    candidates = sorted(
        reports.glob("modal-network-diagnose-*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise HTTPException(status_code=404, detail="no modal diagnostic reports found")

    latest = candidates[0]
    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"failed to read report: {exc}") from exc

    return {
        "report_path": str(latest),
        "classification": data.get("classification"),
        "generated_at": data.get("generated_at"),
        "recommendations": data.get("recommendations", []),
        "proxy_env": data.get("proxy_env", {}),
    }


@app.get("/modal/workflow")
def modal_workflow() -> Dict:
    """Static contract: where Modal vs local work happens (for Cursor agents on Windows/Linux)."""
    return workflow_manifest()


@app.post("/bridge/correlations")
def bridge_correlations(
    payload: CorrelationPayload, x_signature: str = Header(default="")
) -> Dict:
    if not x_signature:
        raise HTTPException(status_code=401, detail="missing signature")
    try:
        secret = get_bridge_secret()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    raw_payload = payload.model_dump()
    if not verify_payload_signature(raw_payload, x_signature, secret):
        raise HTTPException(status_code=401, detail="invalid signature")

    decision = policy.evaluate(raw_payload)
    event = {
        "ts": time.time(),
        "received_from": payload.source,
        "payload": raw_payload,
        "decision": {"label": decision.label, "reason": decision.reason},
    }
    bridge_events.append(event)
    journal.append(event)
    return {"ok": True, "decision": event["decision"]}


@app.get("/bridge/events")
def bridge_recent_events(count: int = 50) -> List[Dict]:
    return list(bridge_events)[-count:]


@app.get("/cleanup/plan")
def cleanup_plan() -> Dict:
    result = cleaner.run(dry_run=True)
    cleanup_runs.append({"ts": time.time(), "mode": "plan", "result": result})
    return result


@app.post("/cleanup/run")
def cleanup_run(confirm: bool = False, dry_run: bool = True) -> Dict:
    if not confirm:
        raise HTTPException(status_code=400, detail="set confirm=true to run cleanup")
    result = cleaner.run(dry_run=dry_run)
    cleanup_runs.append({"ts": time.time(), "mode": "run", "result": result})
    return result


@app.get("/cleanup/history")
def cleanup_history(count: int = 20) -> List[Dict]:
    return list(cleanup_runs)[-count:]


@app.get("/physics/state")
def physics_state() -> Dict:
    return physics.capture()


@app.get("/primitive/state")
def primitive_state_endpoint() -> Dict:
    return primitive_state()


@app.get("/primitive/language")
def primitive_language_endpoint() -> Dict:
    return primitive_language()


@app.get("/primitive/problems")
def primitive_problems_endpoint() -> List[Dict]:
    return solved_minimal_problems()


@app.get("/mini", response_class=HTMLResponse)
def mini_dashboard() -> str:
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Jetspace Mini Monitor</title>
  <style>
    body { margin:0; background:#0d1117; color:#e6edf3; font-family:Consolas,monospace; }
    .box { max-width:460px; margin:24px auto; padding:16px; border:1px solid #30363d; border-radius:10px; background:#161b22; }
    .row { display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dashed #30363d; }
    .row:last-child { border-bottom:none; }
    .muted { color:#8b949e; font-size:12px; margin-top:12px; }
  </style>
</head>
<body>
  <div class="box">
    <div class="row"><span>CPU</span><span id="cpu">--</span></div>
    <div class="row"><span>RAM</span><span id="ram">--</span></div>
    <div class="row"><span>Disk</span><span id="disk">--</span></div>
    <div class="row"><span>Pressure</span><span id="pressure">--</span></div>
    <div class="row"><span>Free Mem (GB)</span><span id="mem">--</span></div>
    <div class="row"><span>Free Disk (GB)</span><span id="freeDisk">--</span></div>
    <div class="muted">localhost-only compact monitor</div>
  </div>
  <script>
    async function tick() {
      try {
        const r = await fetch('/physics/state');
        const d = await r.json();
        document.getElementById('cpu').textContent = d.cpu.toFixed(1) + '%';
        document.getElementById('ram').textContent = d.ram.toFixed(1) + '%';
        document.getElementById('disk').textContent = d.disk.toFixed(1) + '%';
        document.getElementById('pressure').textContent = d.pressure.toFixed(3);
        document.getElementById('mem').textContent = d.free_mem_gb.toFixed(2);
        document.getElementById('freeDisk').textContent = d.free_disk_gb.toFixed(2);
      } catch (e) {}
    }
    setInterval(tick, 1200);
    tick();
  </script>
</body>
</html>
"""


@app.get("/control/state")
def control_state() -> Dict:
    latest = state.latest()
    phys = physics.capture()
    cleanup_plan_result = cleaner.run(dry_run=True)
    return {
        "health": "ok",
        "stats": latest,
        "physics": phys,
        "cleanup_plan": {
            "planned_items": cleanup_plan_result.get("planned_items", 0),
            "reclaimed_bytes": cleanup_plan_result.get("reclaimed_bytes", 0),
            "skipped_due_to_load": cleanup_plan_result.get("skipped_due_to_load", False),
            "skipped_due_to_disk_floor": cleanup_plan_result.get("skipped_due_to_disk_floor", False),
        },
        "bridge_recent_events": len(bridge_events),
    }


@app.get("/control", response_class=HTMLResponse)
def control_panel() -> str:
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Jetspace Control Panel</title>
  <style>
    body { margin:0; background:#0b1020; color:#e6edf3; font-family:Consolas,monospace; }
    .container { max-width:960px; margin:18px auto; padding:0 12px; }
    .top { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
    .muted { color:#9aa6b2; font-size:12px; }
    .grid { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:10px; }
    .card { background:#131a33; border:1px solid #2a3350; border-radius:10px; padding:12px; }
    .val { font-size:24px; font-weight:700; }
    .row { display:flex; justify-content:space-between; margin:6px 0; }
    .actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
    button { background:#1f6feb; color:white; border:none; border-radius:8px; padding:8px 10px; cursor:pointer; }
    button.secondary { background:#30363d; }
    .log { height:180px; overflow:auto; white-space:pre-wrap; border:1px dashed #2a3350; border-radius:8px; padding:8px; margin-top:8px; }
    @media (max-width: 900px) { .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <div class="container">
    <div class="top">
      <h2>Jetspace Control Panel</h2>
      <div class="muted">localhost-only | lightweight | ethical observe+maintain</div>
    </div>
    <div class="muted">Shortcut: <b>Ctrl+Alt+J</b> refreshes panel. Note: Ctrl+Alt+Delete is OS-reserved on Windows and cannot be captured by web apps.</div>
    <div class="grid" style="margin-top:10px;">
      <div class="card"><div>CPU</div><div class="val" id="cpu">--</div></div>
      <div class="card"><div>RAM</div><div class="val" id="ram">--</div></div>
      <div class="card"><div>Pressure</div><div class="val" id="pressure">--</div></div>
      <div class="card"><div>Disk</div><div class="val" id="disk">--</div></div>
      <div class="card"><div>Free Mem GB</div><div class="val" id="freeMem">--</div></div>
      <div class="card"><div>Free Disk GB</div><div class="val" id="freeDisk">--</div></div>
    </div>
    <div class="card" style="margin-top:10px;">
      <div class="row"><span>Cleanup plan items</span><span id="planItems">--</span></div>
      <div class="row"><span>Potential reclaim MB</span><span id="planReclaim">--</span></div>
      <div class="row"><span>Bridge event buffer</span><span id="bridgeEvents">--</span></div>
      <div class="actions">
        <button onclick="refreshNow()">Refresh</button>
        <button class="secondary" onclick="runCleanup(true)">Dry-run cleanup</button>
        <button onclick="runCleanup(false)">Apply cleanup (gated)</button>
      </div>
      <div class="log" id="log"></div>
    </div>
  </div>
  <script>
    const log = (msg) => {
      const el = document.getElementById("log");
      el.textContent = `[${new Date().toLocaleTimeString()}] ` + msg + "\\n" + el.textContent;
    };
    async function refreshNow() {
      try {
        const r = await fetch('/control/state');
        const d = await r.json();
        document.getElementById('cpu').textContent = d.physics.cpu.toFixed(1) + '%';
        document.getElementById('ram').textContent = d.physics.ram.toFixed(1) + '%';
        document.getElementById('pressure').textContent = d.physics.pressure.toFixed(3);
        document.getElementById('disk').textContent = d.physics.disk.toFixed(1) + '%';
        document.getElementById('freeMem').textContent = d.physics.free_mem_gb.toFixed(2);
        document.getElementById('freeDisk').textContent = d.physics.free_disk_gb.toFixed(2);
        document.getElementById('planItems').textContent = d.cleanup_plan.planned_items;
        document.getElementById('planReclaim').textContent = (d.cleanup_plan.reclaimed_bytes / (1024*1024)).toFixed(1);
        document.getElementById('bridgeEvents').textContent = d.bridge_recent_events;
      } catch (e) {
        log('refresh error: ' + e);
      }
    }
    async function runCleanup(dryRun) {
      try {
        const r = await fetch(`/cleanup/run?confirm=true&dry_run=${dryRun ? 'true' : 'false'}`, { method: 'POST' });
        const d = await r.json();
        if (!r.ok) {
          log('cleanup failed: ' + JSON.stringify(d));
          return;
        }
        log(`cleanup done dry_run=${d.dry_run} reclaimed_mb=${(d.reclaimed_bytes/(1024*1024)).toFixed(1)} skipped_load=${d.skipped_due_to_load}`);
        refreshNow();
      } catch (e) {
        log('cleanup error: ' + e);
      }
    }
    document.addEventListener('keydown', (ev) => {
      if (ev.ctrlKey && ev.altKey && (ev.key === 'j' || ev.key === 'J')) {
        ev.preventDefault();
        refreshNow();
        log('shortcut Ctrl+Alt+J -> refresh');
      }
    });
    setInterval(refreshNow, 2000);
    refreshNow();
    log('panel initialized');
  </script>
</body>
</html>
"""
