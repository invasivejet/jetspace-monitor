"""Windows desktop entry: run the FastAPI control plane and open /control in the default browser.

Build (from repo, with venv + frontend optional):
  .\\scripts\\build-jetspace-exe.ps1

Run unfrozen:
  cd backend && ..\\.venv\\Scripts\\python jetspace_desktop.py
"""

from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path


def _working_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def main() -> None:
    wd = _working_dir()
    os.chdir(wd)

    host = os.getenv("JETSPACE_DESKTOP_HOST", "127.0.0.1")
    port = int(os.getenv("JETSPACE_DESKTOP_PORT", "8010"))

    def open_browser() -> None:
        time.sleep(1.25)
        webbrowser.open(f"http://{host}:{port}/control")

    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level=os.getenv("JETSPACE_UVICORN_LOG_LEVEL", "warning"),
        access_log=os.getenv("JETSPACE_UVICORN_ACCESS_LOG", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
