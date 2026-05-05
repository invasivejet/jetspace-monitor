"""Modal runtime telemetry: explicit CPU vs GPU worker semantics.

Run (from repo root, any OS with Modal CLI configured):
  modal run modal/runtime_telemetry.py

Remote functions return only diagnostic fields (no secrets).
"""

from __future__ import annotations

import os
import platform
import subprocess

import modal

app = modal.App("jetspace-runtime-telemetry")


@app.function()
def remote_cpu_telemetry() -> dict:
    uname = os.uname() if hasattr(os, "uname") else None
    return {
        "execution_tier": "modal_remote_cpu",
        "cpu_count": os.cpu_count(),
        "machine": platform.machine(),
        "system": platform.system(),
        "python_version": platform.python_version(),
        "node": platform.node(),
        "uname_sysname": getattr(uname, "sysname", None) if uname else None,
        "uname_release": getattr(uname, "release", None) if uname else None,
    }


@app.function(gpu=["T4", "any"])
def remote_gpu_telemetry() -> dict:
    payload: dict = {"execution_tier": "modal_remote_gpu"}
    try:
        listing = subprocess.run(
            ["nvidia-smi", "-L"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        payload["nvidia_smi_list"] = listing.stdout.strip() if listing.returncode == 0 else None
    except Exception as exc:
        payload["nvidia_smi_list_error"] = str(exc)
    try:
        detail = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=12,
        )
        payload["nvidia_smi_csv"] = detail.stdout.strip() if detail.returncode == 0 else None
    except Exception as exc:
        payload["nvidia_smi_csv_error"] = str(exc)
    return payload


@app.local_entrypoint()
def main() -> None:
    print("remote_cpu_telemetry:", remote_cpu_telemetry.remote())
    try:
        print("remote_gpu_telemetry:", remote_gpu_telemetry.remote())
    except Exception as exc:
        print("remote_gpu_telemetry_skipped:", exc)
