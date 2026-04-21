"""Track dependencies between vault keys.

Allows marking that one key depends on another, so that when a key
is rotated or changed, dependent keys can be flagged for review.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _dep_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".deps.json")


def _load(vault_path: str) -> Dict[str, List[str]]:
    p = _dep_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: Dict[str, List[str]]) -> None:
    _dep_path(vault_path).write_text(json.dumps(data, indent=2))


def add_dependency(vault_path: str, key: str, depends_on: str, vault) -> None:
    """Record that *key* depends on *depends_on*."""
    keys = vault.list_keys()
    if key not in keys:
        raise KeyError(f"Key '{key}' not found in vault")
    if depends_on not in keys:
        raise KeyError(f"Key '{depends_on}' not found in vault")
    if key == depends_on:
        raise ValueError("A key cannot depend on itself")
    data = _load(vault_path)
    deps = data.setdefault(key, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save(vault_path, data)


def remove_dependency(vault_path: str, key: str, depends_on: str) -> bool:
    """Remove a dependency. Returns True if it existed."""
    data = _load(vault_path)
    deps = data.get(key, [])
    if depends_on not in deps:
        return False
    deps.remove(depends_on)
    if not deps:
        del data[key]
    _save(vault_path, data)
    return True


def get_dependencies(vault_path: str, key: str) -> List[str]:
    """Return keys that *key* directly depends on."""
    return list(_load(vault_path).get(key, []))


def get_dependents(vault_path: str, key: str) -> List[str]:
    """Return keys that directly depend on *key*."""
    data = _load(vault_path)
    return [k for k, deps in data.items() if key in deps]


def all_dependencies(vault_path: str) -> Dict[str, List[str]]:
    """Return the full dependency map."""
    return dict(_load(vault_path))
