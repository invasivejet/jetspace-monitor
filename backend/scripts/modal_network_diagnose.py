import json
import os
import socket
import ssl
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from jetspace_paths import reports_dir

REPORT_DIR = reports_dir()
TARGETS = [
    ("api.modal.com", 443),
    ("modal.com", 443),
]


def check_dns(host: str) -> dict:
    """Best-effort DNS resolution with multiple strategies (WSL resolvers can be flaky)."""

    attempts: list[dict] = []

    def record(ok: bool, method: str, detail: dict) -> None:
        attempts.append({"ok": ok, "method": method, **detail})

    # Strategy A: legacy gethostbyname (often IPv4-only)
    try:
        ip = socket.gethostbyname(host)
        record(True, "gethostbyname", {"ips": [ip]})
        return {"ok": True, "ips": [ip], "attempts": attempts}
    except Exception as exc:
        record(False, "gethostbyname", {"error": str(exc)})

    # Strategy B: getaddrinfo (IPv4/IPv6)
    try:
        infos = socket.getaddrinfo(host, None)
        ips = sorted({x[4][0] for x in infos if x[4]})
        if ips:
            record(True, "getaddrinfo", {"ips": ips})
            return {"ok": True, "ips": ips, "attempts": attempts}
        record(False, "getaddrinfo", {"error": "no addresses returned"})
    except Exception as exc:
        record(False, "getaddrinfo", {"error": str(exc)})

    # Strategy C: tiny retry (transient WSL resolver hiccups)
    time.sleep(0.25)
    try:
        ip = socket.gethostbyname(host)
        record(True, "gethostbyname_retry", {"ips": [ip]})
        return {"ok": True, "ips": [ip], "attempts": attempts}
    except Exception as exc:
        record(False, "gethostbyname_retry", {"error": str(exc)})

    return {"ok": False, "ips": [], "attempts": attempts}


def check_tls(host: str, port: int) -> dict:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=6) as s:
            with ctx.wrap_socket(s, server_hostname=host) as t:
                cert = t.getpeercert()
                return {
                    "ok": True,
                    "tls_version": t.version(),
                    "subject": cert.get("subject", []),
                    "issuer": cert.get("issuer", []),
                }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_http(url: str) -> dict:
    try:
        with urlopen(url, timeout=8) as r:
            return {"ok": True, "status": r.status}
    except URLError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def run_cmd(cmd: list[str]) -> dict:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=15)
        return {"ok": True, "output": out.strip()}
    except subprocess.CalledProcessError as exc:
        return {"ok": False, "output": exc.output.strip(), "code": exc.returncode}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def classify(payload: dict) -> str:
    dns_ok = all(x["dns"]["ok"] for x in payload["targets"])
    tls_ok = all(x["tls"]["ok"] for x in payload["targets"])
    modal_ping = payload["modal_cli"]["ok"]
    api_http_ok = bool(payload.get("api_http_probe", {}).get("ok"))

    if dns_ok and tls_ok and modal_ping:
        return "healthy"

    # If application-layer HTTPS works, don't call this "dns-failure" — the failure is narrower
    # (often a flaky resolver path, IPv6 oddities, or a partial probe mismatch).
    if (not dns_ok) and api_http_ok and tls_ok:
        return "dns-probe-degraded"

    if not dns_ok:
        return "dns-failure"

    if dns_ok and not tls_ok:
        return "tls-or-firewall-failure"

    return "modal-cli-or-proxy-failure"


def recommendations(kind: str) -> list[str]:
    mapping = {
        "healthy": [
            "Modal connectivity is healthy. Retry your modal command.",
            "Keep proxy vars minimal and consistent.",
        ],
        "dns-probe-degraded": [
            "HTTPS to api.modal.com succeeded, but one DNS probe path failed — treat this as flaky DNS tooling, not a hard outage.",
            "If this happens often in WSL: check /etc/resolv.conf generation, VPN split-DNS, and try `wsl --shutdown`.",
            "Compare: `python -c \"import socket; print(socket.getaddrinfo('api.modal.com', 443))\"` vs `getent hosts api.modal.com`.",
        ],
        "dns-failure": [
            "Check /etc/resolv.conf and WSL DNS settings.",
            "Try: wsl --shutdown then reopen Ubuntu.",
            "Test: nslookup api.modal.com",
        ],
        "tls-or-firewall-failure": [
            "Verify outbound 443 is allowed by firewall/security software.",
            "Inspect corporate/VPN TLS interception behavior.",
            "Test from browser and curl to https://api.modal.com.",
        ],
        "modal-cli-or-proxy-failure": [
            "Check proxy env vars: HTTP_PROXY/HTTPS_PROXY/NO_PROXY.",
            "Run: modal profile current and modal app list.",
            "If using proxy, include api.modal.com in allowed egress rules.",
        ],
    }
    return mapping.get(kind, ["Collect logs and retry with clean shell environment."])


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    target_results = []
    for host, port in TARGETS:
        target_results.append(
            {
                "host": host,
                "port": port,
                "dns": check_dns(host),
                "tls": check_tls(host, port),
            }
        )

    proxy_env = {
        k: v
        for k, v in os.environ.items()
        if k.lower() in {"http_proxy", "https_proxy", "no_proxy", "all_proxy"}
    }

    modal_profile = run_cmd(["modal", "profile", "current"])
    modal_app_list = run_cmd(["modal", "app", "list"])
    api_http = check_http("https://api.modal.com")

    payload = {
        "generated_at": datetime.now().isoformat(),
        "proxy_env": proxy_env,
        "targets": target_results,
        "api_http_probe": api_http,
        "modal_cli": {
            "ok": modal_profile.get("ok", False) and modal_app_list.get("ok", False),
            "profile": modal_profile,
            "app_list": modal_app_list,
        },
    }
    payload["classification"] = classify(payload)
    payload["recommendations"] = recommendations(payload["classification"])

    out = REPORT_DIR / f"modal-network-diagnose-{ts}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "report": str(out), "classification": payload["classification"]}, indent=2))


if __name__ == "__main__":
    main()
