"""Semantic Modal workflow contract for Jetspace.

This module is import-safe without the `modal` package: it only describes where work runs
and how to invoke the CLI. Cursor agents on Windows and Linux should treat this as the
single source of truth for operation *tier* (local vs Modal container CPU vs Modal GPU).
"""

from __future__ import annotations

import subprocess
from typing import Any, Dict, List

CONTRACT_VERSION = "1.0.0"

# Where code executes (semantic labels for agents and audits)
TIER_LOCAL_SHELL = "local_shell"
TIER_LOCAL_FASTAPI = "local_fastapi"
TIER_MODAL_REMOTE_CPU = "modal_remote_cpu"
TIER_MODAL_REMOTE_GPU = "modal_remote_gpu"


def workflow_manifest() -> Dict[str, Any]:
    root_marker = "Set JETSPACE_ROOT if the repo is not auto-discovered."
    return {
        "contract_version": CONTRACT_VERSION,
        "notes": [
            "Local Cursor / PowerShell / bash runs orchestration; Modal runs isolated container functions on Modal infrastructure.",
            "Secrets never belong in repo or chat: use `modal secret` and Modal dashboard.",
            root_marker,
        ],
        "environment": {
            "JETSPACE_ROOT": "Repository root (optional; auto-detected from backend/jetspace_paths.py).",
            "JETSPACE_REPORTS_DIR": "Override for report JSON/MD/PDF output.",
            "JETSPACE_API_BASE": "Local control API, default http://127.0.0.1:8010.",
        },
        "operations": _operations_table(),
    }


def _operations_table() -> List[Dict[str, Any]]:
    return [
        {
            "id": "modal_cli_auth",
            "tier": TIER_LOCAL_SHELL,
            "description": "Browser-based Modal login and token storage via `python -m modal setup`.",
            "side_effects": "Writes Modal credentials under the user account running the command (per OS).",
        },
        {
            "id": "modal_run_get_started",
            "tier": TIER_MODAL_REMOTE_CPU,
            "entry": "modal/get_started.py",
            "description": "Sanity check: trivial CPU function (`square`) on Modal workers.",
        },
        {
            "id": "modal_run_secret_probe",
            "tier": TIER_MODAL_REMOTE_CPU,
            "entry": "modal/secret_probe.py",
            "description": "Verifies named secret presence; returns lengths/booleans only.",
        },
        {
            "id": "modal_run_runtime_telemetry",
            "tier": TIER_MODAL_REMOTE_CPU,
            "entry": "modal/runtime_telemetry.py",
            "description": "Structured CPU snapshot; optional GPU worker snapshot (T4/any fallback).",
            "gpu_tier": TIER_MODAL_REMOTE_GPU,
        },
        {
            "id": "network_diagnose",
            "tier": TIER_LOCAL_SHELL,
            "entry": "backend/scripts/modal_network_diagnose.py",
            "description": "Local DNS/TLS/HTTP/Modal CLI probes; writes JSON under reports/.",
        },
        {
            "id": "harmony_audit",
            "tier": TIER_LOCAL_SHELL,
            "entry": "backend/scripts/harmony_audit.py",
            "description": "Pulls local FastAPI physics/control; includes Modal CLI probe metadata.",
        },
    ]


def _run_modal(args: List[str], timeout: float) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            ["modal", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    except FileNotFoundError:
        return {"ok": False, "error": "modal CLI not found on PATH"}
    except subprocess.TimeoutExpired as exc:
        return {"ok": False, "error": f"timeout: {exc}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def probe_modal_stack() -> Dict[str, Any]:
    """Local-shell probes of the Modal CLI (does not schedule remote functions)."""

    profile = _run_modal(["profile", "current"], timeout=12.0)
    apps = _run_modal(["app", "list"], timeout=20.0)
    ok = bool(profile.get("ok") and apps.get("ok"))
    return {
        "execution_context": TIER_LOCAL_SHELL,
        "contract_version": CONTRACT_VERSION,
        "ok": ok,
        "profile": profile,
        "app_list": apps,
    }
