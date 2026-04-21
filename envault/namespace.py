"""Namespace support for grouping vault keys under logical prefixes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_NAMESPACE_FILE = ".envault_namespaces.json"


def _ns_path(vault_path: str) -> Path:
    return Path(vault_path).parent / _NAMESPACE_FILE


def _load(vault_path: str) -> Dict[str, str]:
    """Return mapping of key -> namespace."""
    p = _ns_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: Dict[str, str]) -> None:
    _ns_path(vault_path).write_text(json.dumps(data, indent=2))


def assign_namespace(vault_path: str, key: str, namespace: str) -> None:
    """Assign *key* to *namespace*. Raises KeyError if key not in vault."""
    from envault.vault import Vault  # avoid circular at module level

    v = Vault(vault_path)
    if key not in v.list_keys():
        raise KeyError(f"Key '{key}' not found in vault")
    if not namespace.isidentifier():
        raise ValueError(f"Namespace '{namespace}' is not a valid identifier")
    data = _load(vault_path)
    data[key] = namespace
    _save(vault_path, data)


def remove_namespace(vault_path: str, key: str) -> bool:
    """Remove namespace assignment for *key*. Returns True if removed."""
    data = _load(vault_path)
    if key not in data:
        return False
    del data[key]
    _save(vault_path, data)
    return True


def get_namespace(vault_path: str, key: str) -> Optional[str]:
    """Return namespace for *key*, or None if unassigned."""
    return _load(vault_path).get(key)


def keys_in_namespace(vault_path: str, namespace: str) -> List[str]:
    """Return all keys assigned to *namespace*."""
    data = _load(vault_path)
    return [k for k, ns in data.items() if ns == namespace]


def list_namespaces(vault_path: str) -> Dict[str, List[str]]:
    """Return a mapping of namespace -> [keys] for all assigned keys."""
    data = _load(vault_path)
    result: Dict[str, List[str]] = {}
    for key, ns in data.items():
        result.setdefault(ns, []).append(key)
    return result
