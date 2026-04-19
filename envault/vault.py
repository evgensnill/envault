"""Vault storage: read/write encrypted secrets to a JSON file."""

import json
from pathlib import Path
from typing import Dict

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_PATH = Path(".envault.json")


class Vault:
    def __init__(self, path: Path = DEFAULT_VAULT_PATH):
        self.path = path
        self._data: Dict[str, str] = {}

    def load(self, password: str) -> None:
        """Load and decrypt all secrets from disk."""
        if not self.path.exists():
            self._data = {}
            return
        raw = json.loads(self.path.read_text())
        self._data = {k: decrypt(v, password) for k, v in raw.items()}

    def save(self, password: str) -> None:
        """Encrypt all secrets and persist to disk."""
        encrypted = {k: encrypt(v, password) for k, v in self._data.items()}
        self.path.write_text(json.dumps(encrypted, indent=2))

    def set(self, key: str, value: str) -> None:
        """Set a secret value."""
        self._data[key] = value

    def get(self, key: str) -> str:
        """Retrieve a secret value."""
        if key not in self._data:
            raise KeyError(f"Secret '{key}' not found.")
        return self._data[key]

    def delete(self, key: str) -> None:
        """Remove a secret."""
        if key not in self._data:
            raise KeyError(f"Secret '{key}' not found.")
        del self._data[key]

    def list_keys(self) -> list:
        """Return all secret keys."""
        return list(self._data.keys())
