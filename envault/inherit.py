"""Vault inheritance: allow a vault to inherit keys from a parent vault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_INHERIT_FILE = ".envault_inherit.json"


def _inherit_path(vault_path: Path) -> Path:
    return vault_path.parent / _INHERIT_FILE


def _load(vault_path: Path) -> Dict:
    p = _inherit_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: Path, data: Dict) -> None:
    _inherit_path(vault_path).write_text(json.dumps(data, indent=2))


def set_parent(vault_path: Path, parent_path: str) -> None:
    """Set the parent vault path for inheritance."""
    parent = Path(parent_path).resolve()
    if not parent.exists():
        raise FileNotFoundError(f"Parent vault not found: {parent}")
    data = _load(vault_path)
    data["parent"] = str(parent)
    _save(vault_path, data)


def get_parent(vault_path: Path) -> Optional[str]:
    """Return the configured parent vault path, or None."""
    return _load(vault_path).get("parent")


def clear_parent(vault_path: Path) -> bool:
    """Remove the parent vault configuration. Returns True if removed."""
    data = _load(vault_path)
    if "parent" not in data:
        return False
    del data["parent"]
    _save(vault_path, data)
    return True


def resolve_key(vault, key: str, password: str) -> Optional[str]:
    """Look up *key* in *vault*; fall back to parent vault if not found.

    Parameters
    ----------
    vault:
        An open :class:`envault.vault.Vault` instance.
    key:
        The secret key to look up.
    password:
        Master password used to open the parent vault (same password assumed).
    """
    try:
        return vault.get(key)
    except KeyError:
        pass

    parent_path = get_parent(Path(vault.path))
    if parent_path is None:
        raise KeyError(key)

    from envault.vault import Vault  # local import to avoid circular deps

    parent_vault = Vault(parent_path, password)
    parent_vault.load()
    return parent_vault.get(key)


def effective_keys(vault, password: str) -> List[str]:
    """Return combined key list from *vault* and its parent (if any)."""
    keys = set(vault.list_keys())

    parent_path = get_parent(Path(vault.path))
    if parent_path is None:
        return sorted(keys)

    from envault.vault import Vault

    parent_vault = Vault(parent_path, password)
    parent_vault.load()
    keys.update(parent_vault.list_keys())
    return sorted(keys)
