import json
from pathlib import Path

from cryptography.fernet import Fernet


class EncryptedJournal:
    def __init__(self, key_path: Path, log_path: Path) -> None:
        self.key_path = key_path
        self.log_path = log_path
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._fernet = Fernet(self._ensure_key())

    def _ensure_key(self) -> bytes:
        if self.key_path.exists():
            return self.key_path.read_bytes().strip()
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)
        return key

    def append(self, event: dict) -> None:
        plaintext = json.dumps(event, separators=(",", ":"), sort_keys=True).encode("utf-8")
        encrypted = self._fernet.encrypt(plaintext)
        with self.log_path.open("ab") as f:
            f.write(encrypted + b"\n")

