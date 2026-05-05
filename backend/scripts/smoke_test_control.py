import json
import urllib.parse
import urllib.request


BASE = "http://127.0.0.1:8010"


def get(path: str):
    with urllib.request.urlopen(BASE + path, timeout=8) as r:
        return r.status, r.read().decode("utf-8")


def post(path: str):
    req = urllib.request.Request(BASE + path, method="POST")
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.status, r.read().decode("utf-8")


def main() -> None:
    checks = []

    for p in ["/health", "/physics/state", "/primitive/language", "/primitive/problems", "/control", "/control/state"]:
        status, body = get(p)
        checks.append((p, status, len(body)))

    status, body = post("/cleanup/run?confirm=true&dry_run=true")
    dry = json.loads(body)
    checks.append(("/cleanup/run dry", status, dry.get("dry_run")))

    status, body = post("/cleanup/run?confirm=true&dry_run=false")
    apply_res = json.loads(body)
    checks.append(("/cleanup/run apply", status, apply_res.get("skipped_due_to_load")))

    print(json.dumps({"ok": True, "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
