import json
import os
import platform
import socket
import sys
import time
import textwrap
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import psutil

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from jetspace_paths import reports_dir
from modal_workflow import probe_modal_stack

API_BASE = os.getenv("JETSPACE_API_BASE", "http://127.0.0.1:8010")
REPORT_DIR = reports_dir()


def fetch_json(path: str):
    try:
        with urlopen(f"{API_BASE}{path}", timeout=4) as r:
            return json.loads(r.read().decode("utf-8"))
    except URLError:
        return None
    except Exception:
        return None


def modal_probe():
    return probe_modal_stack()


def battery_probe():
    # WSL/Ubuntu-side battery probe
    bat_root = Path("/sys/class/power_supply")
    bats = sorted([p for p in bat_root.glob("BAT*") if p.is_dir()])
    if not bats:
        return {"available": False}
    b = bats[0]
    try:
        capacity = float((b / "capacity").read_text().strip())
        status = (b / "status").read_text().strip()
        return {"available": True, "capacity_percent": capacity, "status": status}
    except Exception:
        return {"available": False}


def classify_root_cause(phys: dict) -> str:
    if not phys:
        return "unknown"
    cpu = phys.get("cpu", 0.0)
    ram = phys.get("ram", 0.0)
    disk = phys.get("disk", 0.0)
    free_disk = phys.get("free_disk_gb")
    free_mem = phys.get("free_mem_gb")
    d2 = abs(phys.get("d2_cpu", 0.0))

    if free_disk is not None and float(free_disk) < 3.0:
        return "storage-bound pressure"
    if disk > 92:
        return "storage-bound pressure"
    if free_mem is not None and float(free_mem) < 2.0 and ram > 72:
        return "memory-bound pressure"
    if ram > 85:
        return "memory-bound pressure"
    if cpu > 85 and d2 > 10:
        return "compute-bound volatility"
    if disk > 90:
        return "storage-bound pressure"
    return "balanced/stable"


def render_markdown(payload: dict) -> str:
    phys = payload.get("physics") or {}
    control = payload.get("control") or {}
    primitive = payload.get("primitive") or {}
    interpretation = payload.get("interpretation", {})
    modal = payload.get("modal", {})
    battery = payload.get("battery", {})
    return f"""# Jetspace Harmony Audit

- Generated: {payload["generated_at"]}
- Host: {payload["host"]}
- Platform: {payload["platform"]}
- API base: {payload["api_base"]}

## Executive Summary

- Root-cause classification: **{interpretation.get("root_cause", "unknown")}**
- Pressure score: **{phys.get("pressure", "n/a")}**
- Cleanup planned reclaim (MB): **{(control.get("cleanup_plan", {}).get("reclaimed_bytes", 0) / (1024*1024)):.1f}**
- Modal CLI status: **{"ok" if modal.get("ok") else "degraded"}** (local shell → Modal API; not remote GPU/CPU workers)

## Physics Invariants

- State manifold: CPU={phys.get("cpu")} RAM={phys.get("ram")} DISK={phys.get("disk")}
- Flow terms: d_cpu={phys.get("d_cpu")} d_ram={phys.get("d_ram")} d2_cpu={phys.get("d2_cpu")}
- Reserve variables: free_mem_gb={phys.get("free_mem_gb")} free_disk_gb={phys.get("free_disk_gb")}

## Primitive Computational Language

- Memory: active state manifold.
- CPU: discrete symbolic transform engine.
- GPU: parallel field evaluator (if available).
- PRNG: entropy probe -> {primitive.get("prng_probe")}
- Hamiltonian step: {primitive.get("discrete_hamiltonian")}

## Ethical and Operational Constraints

- Localhost-only monitoring/control plane.
- Guarded cleanup: dry-run first, pressure-gated apply.
- No covert exfiltration behaviors.
- Security posture: secrets must be rotated if exposed.

## WSL + Windows Harmony Signals

- API reachable: {payload.get("api_reachable")}
- Battery probe: {battery}
- Modal stack probe: {modal}

## Recommended Next Action

{interpretation.get("next_action", "Maintain current policy and re-audit in 1 hour.")}
"""


def write_pdf(md_text: str, out_pdf: Path) -> str:
    # Try reportlab first (most robust), then fpdf2.
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(out_pdf), pagesize=letter)
        width, height = letter
        x = 50
        y = height - 50
        c.setFont("Helvetica", 11)

        for raw in md_text.splitlines():
            line = raw.encode("ascii", errors="replace").decode("ascii")
            wrapped = textwrap.wrap(line, width=105, break_long_words=True, break_on_hyphens=True) or [""]
            for w in wrapped:
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y = height - 50
                c.drawString(x, y, w)
                y -= 14
        c.save()
        return "pdf_ok_reportlab"
    except Exception:
        pass

    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=12)
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        for line in md_text.splitlines():
            if line.startswith("# "):
                pdf.set_font("Helvetica", style="B", size=15)
                pdf.multi_cell(0, 8, line[2:])
                pdf.set_font("Helvetica", size=11)
            elif line.startswith("## "):
                pdf.ln(1)
                pdf.set_font("Helvetica", style="B", size=12)
                pdf.multi_cell(0, 7, line[3:])
                pdf.set_font("Helvetica", size=11)
            else:
                line = line.encode("ascii", errors="replace").decode("ascii")
                wrapped = textwrap.wrap(line, width=95, break_long_words=True, break_on_hyphens=True) or [""]
                for w in wrapped:
                    pdf.multi_cell(0, 6, w)
        pdf.output(str(out_pdf))
        return "pdf_ok_fpdf2"
    except Exception as exc:
        out_pdf.write_text("PDF generation failed. See markdown report.\n\n" + str(exc), encoding="utf-8")
        return f"pdf_fallback: {exc}"


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    phys = fetch_json("/physics/state")
    control = fetch_json("/control/state")
    primitive = fetch_json("/primitive/state")
    api_reachable = bool(phys and control and primitive)

    modal = modal_probe()
    battery = battery_probe()
    root = classify_root_cause(phys or {})

    next_action = {
        "memory-bound pressure": "Increase cleanup cadence in dry-run mode and close high-RAM background apps.",
        "compute-bound volatility": "Reduce monitoring refresh rate or nonessential workloads.",
        "storage-bound pressure": "Run bounded cleanup apply during low-pressure window.",
        "balanced/stable": "Keep current policy; no emergency intervention required.",
        "unknown": "Ensure API is up, then rerun audit.",
    }.get(root, "Keep conservative operation.")

    payload = {
        "generated_at": datetime.now().isoformat(),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "api_base": API_BASE,
        "api_reachable": api_reachable,
        "physics": phys,
        "control": control,
        "primitive": primitive,
        "modal": modal,
        "battery": battery,
        "interpretation": {
            "root_cause": root,
            "next_action": next_action,
        },
    }

    json_path = REPORT_DIR / f"harmony-audit-{ts}.json"
    md_path = REPORT_DIR / f"harmony-audit-{ts}.md"
    pdf_path = REPORT_DIR / f"harmony-audit-{ts}.pdf"

    md = render_markdown(payload)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    pdf_status = write_pdf(md, pdf_path)

    print(
        json.dumps(
            {
                "ok": True,
                "json": str(json_path),
                "markdown": str(md_path),
                "pdf": str(pdf_path),
                "pdf_status": pdf_status,
                "root_cause": payload["interpretation"]["root_cause"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
