import os
import sys
import time
import json
from pathlib import Path
import ssl
import urllib.request

import psutil

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bridge.security import sign_payload


def sample_payload() -> dict:
    cpu = psutil.cpu_percent(interval=0.2)
    ram = psutil.virtual_memory().percent
    return {
        "source": "ubuntu",
        "ts": time.time(),
        "state": {"cpu": cpu, "ram": ram},
        "d_state": {"d_cpu": 0.0, "d_ram": 0.0},
        "anomaly_score": 0.2,
        "confidence": 0.7,
    }


def main() -> None:
    secret = os.getenv("JETSPACE_BRIDGE_SHARED_SECRET", "")
    if not secret:
        raise RuntimeError("Set JETSPACE_BRIDGE_SHARED_SECRET before running sender.")

    payload = sample_payload()
    signature = sign_payload(payload, secret.encode("utf-8"))

    cert_dir = Path(__file__).resolve().parents[1] / "certs"
    context = ssl.create_default_context(cafile=str(cert_dir / "ca.crt"))
    context.load_cert_chain(certfile=str(cert_dir / "client.crt"), keyfile=str(cert_dir / "client.key"))

    req = urllib.request.Request(
        "https://127.0.0.1:8443/bridge/correlations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-signature": signature,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, context=context) as response:
        print(response.read().decode())


if __name__ == "__main__":
    main()
