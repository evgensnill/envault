"""Vault changelog: track set/delete/rotate events per key."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional


def _changelog_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".changelog.json")


def _load(vault_path: str) -> List[Dict[str, Any]]:
    p = _changelog_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(vault_path: str, entries: List[Dict[str, Any]]) -> None:
    _changelog_path(vault_path).write_text(json.dumps(entries, indent=2))


def record_change(
    vault_path: str,
    key: str,
    action: str,
    actor: Optional[str] = None,
    note: Optional[str] = None,
) -> None:
    """Append a change entry. action should be 'set', 'delete', or 'rotate'."""
    if action not in ("set", "delete", "rotate"):
        raise ValueError(f"Invalid action: {action!r}")
    entries = _load(vault_path)
    entries.append({
        "key": key,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "note": note,
    })
    _save(vault_path, entries)


def get_history(
    vault_path: str,
    key: Optional[str] = None,
    action: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return changelog entries, optionally filtered by key and/or action."""
    entries = _load(vault_path)
    if key:
        entries = [e for e in entries if e["key"] == key]
    if action:
        entries = [e for e in entries if e["action"] == action]
    if limit:
        entries = entries[-limit:]
    return entries


def clear_history(vault_path: str) -> None:
    """Remove all changelog entries."""
    _save(vault_path, [])


def get_last_change(
    vault_path: str,
    key: str,
) -> Optional[Dict[str, Any]]:
    """Return the most recent changelog entry for the given key, or None if not found."""
    entries = _load(vault_path)
    for entry in reversed(entries):
        if entry["key"] == key:
            return entry
    return None
