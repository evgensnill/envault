"""Watermark support: embed and verify a hidden identity marker in vault secrets."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

_WATERMARK_KEY = "__envault_watermark__"


def _wm_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".watermark.json")


def _load(vault_path: str) -> dict:
    p = _wm_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _wm_path(vault_path).write_text(json.dumps(data, indent=2))


def set_watermark(vault_path: str, identity: str) -> str:
    """Embed a watermark for *identity* into the vault metadata.

    Returns the watermark token.
    """
    token = hashlib.sha256(f"{vault_path}:{identity}".encode()).hexdigest()[:16]
    data = _load(vault_path)
    data["identity"] = identity
    data["token"] = token
    _save(vault_path, data)
    return token


def get_watermark(vault_path: str) -> Optional[dict]:
    """Return the watermark record or *None* if none is set."""
    data = _load(vault_path)
    if not data:
        return None
    return {"identity": data.get("identity"), "token": data.get("token")}


def verify_watermark(vault_path: str, identity: str) -> bool:
    """Return *True* when the stored token matches *identity*."""
    data = _load(vault_path)
    if not data:
        return False
    expected = hashlib.sha256(f"{vault_path}:{identity}".encode()).hexdigest()[:16]
    return data.get("token") == expected and data.get("identity") == identity


def remove_watermark(vault_path: str) -> bool:
    """Delete the watermark file. Returns *True* if it existed."""
    p = _wm_path(vault_path)
    if p.exists():
        p.unlink()
        return True
    return False
