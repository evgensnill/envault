"""Key aliasing: map friendly names to vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _alias_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".aliases.json")


def _load(vault_path: Path) -> Dict[str, str]:
    p = _alias_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: Path, aliases: Dict[str, str]) -> None:
    _alias_path(vault_path).write_text(json.dumps(aliases, indent=2))


def add_alias(vault_path: Path, alias: str, key: str, known_keys: List[str]) -> None:
    """Create an alias pointing to an existing vault key."""
    if key not in known_keys:
        raise KeyError(f"Key '{key}' not found in vault.")
    if not alias.isidentifier():
        raise ValueError(f"Alias '{alias}' is not a valid identifier.")
    aliases = _load(vault_path)
    aliases[alias] = key
    _save(vault_path, aliases)


def remove_alias(vault_path: Path, alias: str) -> bool:
    """Remove an alias. Returns True if it existed."""
    aliases = _load(vault_path)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save(vault_path, aliases)
    return True


def resolve_alias(vault_path: Path, alias: str) -> Optional[str]:
    """Return the vault key for a given alias, or None."""
    return _load(vault_path).get(alias)


def list_aliases(vault_path: Path) -> Dict[str, str]:
    """Return all alias -> key mappings."""
    return _load(vault_path)


def resolve_key(vault_path: Path, name: str, known_keys: List[str]) -> str:
    """Return the real key for *name*, resolving alias if needed."""
    if name in known_keys:
        return name
    resolved = resolve_alias(vault_path, name)
    if resolved is None:
        raise KeyError(f"'{name}' is neither a vault key nor a known alias.")
    return resolved
