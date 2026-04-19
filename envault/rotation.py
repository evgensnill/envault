"""Secret rotation utilities for envault."""
from __future__ import annotations

import datetime
from typing import Optional

ROTATION_META_KEY = "__rotation_meta__"


def get_rotation_meta(vault) -> dict:
    """Return rotation metadata stored inside the vault."""
    try:
        raw = vault.get(ROTATION_META_KEY)
        import json
        return json.loads(raw)
    except Exception:
        return {}


def set_rotation_meta(vault, meta: dict) -> None:
    import json
    vault.set(ROTATION_META_KEY, json.dumps(meta))


def record_rotation(vault, key: str) -> None:
    """Record that *key* was rotated right now."""
    meta = get_rotation_meta(vault)
    meta[key] = datetime.datetime.utcnow().isoformat()
    set_rotation_meta(vault, meta)


def last_rotated(vault, key: str) -> Optional[datetime.datetime]:
    """Return the datetime when *key* was last rotated, or None."""
    meta = get_rotation_meta(vault)
    ts = meta.get(key)
    if ts is None:
        return None
    return datetime.datetime.fromisoformat(ts)


def rotate_key(vault, key: str, new_value: str) -> None:
    """Set a new value for *key* and record the rotation timestamp."""
    vault.set(key, new_value)
    record_rotation(vault, key)


def keys_older_than(vault, days: int) -> list[str]:
    """Return keys whose last rotation is older than *days* days."""
    meta = get_rotation_meta(vault)
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    stale = []
    for key, ts in meta.items():
        try:
            rotated_at = datetime.datetime.fromisoformat(ts)
            if rotated_at < cutoff:
                stale.append(key)
        except ValueError:
            continue
    return stale
