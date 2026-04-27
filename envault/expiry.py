"""Key expiry management: set, check, and list expiring vault keys."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_EXPIRY_FILE = ".envault_expiry.json"


def _expiry_path(vault_path: str) -> Path:
    return Path(vault_path).parent / _EXPIRY_FILE


def _load(vault_path: str) -> dict:
    p = _expiry_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _expiry_path(vault_path).write_text(json.dumps(data, indent=2))


def set_expiry(vault_path: str, key: str, expires_at: datetime) -> None:
    """Set an expiry datetime (UTC) for a vault key."""
    data = _load(vault_path)
    data[key] = expires_at.astimezone(timezone.utc).isoformat()
    _save(vault_path, data)


def get_expiry(vault_path: str, key: str) -> Optional[datetime]:
    """Return the expiry datetime for a key, or None if not set."""
    data = _load(vault_path)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def remove_expiry(vault_path: str, key: str) -> bool:
    """Remove expiry for a key. Returns True if removed, False if not set."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def is_expired(vault_path: str, key: str) -> bool:
    """Return True if the key has an expiry set and it is in the past."""
    expiry = get_expiry(vault_path, key)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def expired_keys(vault_path: str) -> list[str]:
    """Return all keys whose expiry has passed."""
    data = _load(vault_path)
    now = datetime.now(timezone.utc)
    return [
        k for k, v in data.items()
        if datetime.fromisoformat(v) <= now
    ]


def list_expiries(vault_path: str) -> dict[str, datetime]:
    """Return a mapping of key -> expiry datetime for all keys with expiry set."""
    data = _load(vault_path)
    return {k: datetime.fromisoformat(v) for k, v in data.items()}
