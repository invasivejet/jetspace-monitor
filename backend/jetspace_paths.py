"""Canonical filesystem layout for Jetspace (Windows, Linux, WSL).

Override with:
- JETSPACE_ROOT: repository root
- JETSPACE_REPORTS_DIR: report output directory (default: <root>/reports)
"""

from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    env = os.getenv("JETSPACE_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    # This file: <root>/backend/jetspace_paths.py
    return Path(__file__).resolve().parent.parent


def reports_dir() -> Path:
    env = os.getenv("JETSPACE_REPORTS_DIR", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return project_root() / "reports"
