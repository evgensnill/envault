"""Pin management: lock a key to a specific value and prevent accidental overwrites."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

_PINS_FILENAME = ".envault_pins.json"


def _pins_path(vault_path: str) -> Path:
    return Path(vault_path).parent / _PINS_FILENAME


def _load(vault_path: str) -> Dict[str, str]:
    p = _pins_path(vault_path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save(vault_path: str, pins: Dict[str, str]) -> None:
    p = _pins_path(vault_path)
    with p.open("w") as f:
        json.dump(pins, f, indent=2)


def pin_key(vault_path: str, key: str, reason: str = "") -> None:
    """Pin *key* so it cannot be overwritten without an explicit unpin."""
    pins = _load(vault_path)
    pins[key] = reason
    _save(vault_path, pins)


def unpin_key(vault_path: str, key: str) -> bool:
    """Remove pin for *key*. Returns True if the pin existed, False otherwise."""
    pins = _load(vault_path)
    if key not in pins:
        return False
    del pins[key]
    _save(vault_path, pins)
    return True


def is_pinned(vault_path: str, key: str) -> bool:
    """Return True if *key* is currently pinned."""
    return key in _load(vault_path)


def list_pins(vault_path: str) -> List[Dict[str, str]]:
    """Return all pinned keys with their reasons."""
    pins = _load(vault_path)
    return [{"key": k, "reason": v} for k, v in pins.items()]


def assert_not_pinned(vault_path: str, key: str) -> None:
    """Raise ValueError if *key* is pinned."""
    pins = _load(vault_path)
    if key in pins:
        reason = pins[key]
        msg = f"Key '{key}' is pinned and cannot be modified."
        if reason:
            msg += f" Reason: {reason}"
        raise ValueError(msg)
