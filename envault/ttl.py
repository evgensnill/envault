"""TTL (time-to-live) management for vault secrets."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

TTL_FILENAME = ".envault_ttl.json"


def _ttl_path(vault_path: str) -> Path:
    return Path(vault_path).parent / TTL_FILENAME


def _load(vault_path: str) -> dict:
    p = _ttl_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _ttl_path(vault_path).write_text(json.dumps(data, indent=2))


def set_ttl(vault_path: str, key: str, seconds: int) -> None:
    """Assign a TTL (in seconds from now) to *key*."""
    data = _load(vault_path)
    data[key] = {"expires_at": time.time() + seconds, "ttl_seconds": seconds}
    _save(vault_path, data)


def get_ttl(vault_path: str, key: str) -> Optional[dict]:
    """Return TTL metadata for *key*, or None if no TTL is set."""
    return _load(vault_path).get(key)


def remove_ttl(vault_path: str, key: str) -> bool:
    """Remove the TTL for *key*. Returns True if an entry was removed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def is_expired(vault_path: str, key: str) -> bool:
    """Return True if *key* has a TTL that has already elapsed."""
    meta = get_ttl(vault_path, key)
    if meta is None:
        return False
    return time.time() >= meta["expires_at"]


def expired_keys(vault_path: str, keys: list[str]) -> list[str]:
    """Return the subset of *keys* whose TTL has elapsed."""
    return [k for k in keys if is_expired(vault_path, k)]


def list_ttls(vault_path: str) -> dict:
    """Return all TTL records keyed by secret name."""
    return _load(vault_path)
