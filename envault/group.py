"""Key grouping — assign vault keys to named groups for bulk operations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _groups_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".groups.json")


def _load(vault_path: str) -> Dict[str, List[str]]:
    p = _groups_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: Dict[str, List[str]]) -> None:
    _groups_path(vault_path).write_text(json.dumps(data, indent=2))


def add_to_group(vault_path: str, group: str, key: str, vault_keys: List[str]) -> None:
    """Add *key* to *group*. Raises KeyError if key is not in the vault."""
    if key not in vault_keys:
        raise KeyError(f"Key '{key}' not found in vault")
    if not group.isidentifier():
        raise ValueError(f"Invalid group name: '{group}'")
    data = _load(vault_path)
    members = data.setdefault(group, [])
    if key not in members:
        members.append(key)
    _save(vault_path, data)


def remove_from_group(vault_path: str, group: str, key: str) -> bool:
    """Remove *key* from *group*. Returns True if removed, False if not present."""
    data = _load(vault_path)
    members = data.get(group, [])
    if key not in members:
        return False
    members.remove(key)
    if not members:
        del data[group]
    _save(vault_path, data)
    return True


def get_group(vault_path: str, group: str) -> List[str]:
    """Return all keys in *group* (empty list if group does not exist)."""
    return _load(vault_path).get(group, [])


def list_groups(vault_path: str) -> Dict[str, List[str]]:
    """Return a mapping of all group names to their member key lists."""
    return _load(vault_path)


def delete_group(vault_path: str, group: str) -> bool:
    """Delete an entire group. Returns True if it existed."""
    data = _load(vault_path)
    if group not in data:
        return False
    del data[group]
    _save(vault_path, data)
    return True
