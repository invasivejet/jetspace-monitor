import hashlib
import hmac
import json
import os


BRIDGE_SHARED_SECRET_ENV = "JETSPACE_BRIDGE_SHARED_SECRET"


def get_bridge_secret() -> bytes:
    secret = os.getenv(BRIDGE_SHARED_SECRET_ENV, "")
    if not secret:
        raise RuntimeError(f"Missing env var: {BRIDGE_SHARED_SECRET_ENV}")
    return secret.encode("utf-8")


def canonical_json(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: dict, secret: bytes) -> str:
    digest = hmac.new(secret, canonical_json(payload), hashlib.sha256).hexdigest()
    return digest


def verify_payload_signature(payload: dict, provided_sig: str, secret: bytes) -> bool:
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, provided_sig)

