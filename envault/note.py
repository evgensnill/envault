"""Per-key notes: longer-form documentation attached to vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


def _note_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".notes.json")


def _load(vault_path: str) -> dict:
    p = _note_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _note_path(vault_path).write_text(json.dumps(data, indent=2))


def set_note(vault_path: str, key: str, text: str, vault_keys: list[str]) -> None:
    """Attach a note to *key*. Raises KeyError if the key is not in the vault."""
    if key not in vault_keys:
        raise KeyError(f"Key '{key}' not found in vault.")
    if not text:
        raise ValueError("Note text must not be empty.")
    data = _load(vault_path)
    data[key] = {
        "text": text,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save(vault_path, data)


def get_note(vault_path: str, key: str) -> dict | None:
    """Return the note record for *key*, or None if absent."""
    return _load(vault_path).get(key)


def remove_note(vault_path: str, key: str) -> bool:
    """Remove the note for *key*. Returns True if it existed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_notes(vault_path: str) -> dict[str, dict]:
    """Return all note records keyed by vault key."""
    return _load(vault_path)
