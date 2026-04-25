"""Per-key comment/annotation storage for vault entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _comment_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".comments.json")


def _load(vault_path: str) -> dict:
    p = _comment_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _comment_path(vault_path).write_text(json.dumps(data, indent=2))


def set_comment(vault_path: str, key: str, comment: str, vault=None) -> None:
    """Set a comment/annotation for a vault key."""
    if vault is not None and key not in vault.list_keys():
        raise KeyError(f"Key '{key}' does not exist in vault")
    if not comment.strip():
        raise ValueError("Comment must not be empty")
    data = _load(vault_path)
    data[key] = comment.strip()
    _save(vault_path, data)


def get_comment(vault_path: str, key: str) -> Optional[str]:
    """Return the comment for a key, or None if not set."""
    return _load(vault_path).get(key)


def remove_comment(vault_path: str, key: str) -> bool:
    """Remove a comment for a key. Returns True if removed, False if absent."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def list_comments(vault_path: str) -> dict[str, str]:
    """Return all key -> comment mappings."""
    return dict(_load(vault_path))
