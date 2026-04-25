"""Checksum tracking for vault keys — detect unexpected external modifications."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional


def _checksum_path(vault_path: str) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".checksums.json")


def _load(vault_path: str) -> Dict[str, str]:
    path = _checksum_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(vault_path: str, store: Dict[str, str]) -> None:
    _checksum_path(vault_path).write_text(json.dumps(store, indent=2))


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def record_checksum(vault_path: str, key: str, value: str) -> str:
    """Compute and persist the checksum for *key*'s current value."""
    store = _load(vault_path)
    digest = _hash(value)
    store[key] = digest
    _save(vault_path, store)
    return digest


def get_checksum(vault_path: str, key: str) -> Optional[str]:
    """Return the stored checksum for *key*, or None if not recorded."""
    return _load(vault_path).get(key)


def remove_checksum(vault_path: str, key: str) -> bool:
    """Remove the stored checksum for *key*. Returns True if it existed."""
    store = _load(vault_path)
    if key not in store:
        return False
    del store[key]
    _save(vault_path, store)
    return True


def verify_checksum(vault_path: str, key: str, value: str) -> bool:
    """Return True if *value* matches the recorded checksum for *key*.

    Returns False when no checksum has been recorded yet.
    """
    stored = get_checksum(vault_path, key)
    if stored is None:
        return False
    return stored == _hash(value)


def list_checksums(vault_path: str) -> Dict[str, str]:
    """Return a copy of the full checksum store."""
    return dict(_load(vault_path))
