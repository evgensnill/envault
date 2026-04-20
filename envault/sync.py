"""Sync vault secrets to/from environment variable providers (e.g. .env files, shell env)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import Vault


@dataclass
class SyncResult:
    pushed: List[str] = field(default_factory=list)
    pulled: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


def push_to_env(vault: Vault, keys: Optional[List[str]] = None, overwrite: bool = True) -> SyncResult:
    """Write vault secrets into the current process environment."""
    result = SyncResult()
    targets = keys if keys is not None else vault.list_keys()
    for key in targets:
        value = vault.get(key)
        if key in os.environ and not overwrite:
            result.skipped.append(key)
        else:
            os.environ[key] = value
            result.pushed.append(key)
    return result


def pull_from_env(vault: Vault, keys: Optional[List[str]] = None, overwrite: bool = True) -> SyncResult:
    """Read secrets from the current process environment into the vault."""
    result = SyncResult()
    targets = keys if keys is not None else list(os.environ.keys())
    for key in targets:
        if key not in os.environ:
            result.skipped.append(key)
            continue
        env_value = os.environ[key]
        try:
            existing = vault.get(key)
            if existing == env_value:
                result.skipped.append(key)
                continue
            if not overwrite:
                result.conflicts.append(key)
                continue
        except KeyError:
            pass
        vault.set(key, env_value)
        result.pulled.append(key)
    return result


def diff_with_env(vault: Vault, keys: Optional[List[str]] = None) -> Dict[str, dict]:
    """Return a mapping of keys that differ between vault and os.environ."""
    targets = keys if keys is not None else vault.list_keys()
    differences: Dict[str, dict] = {}
    for key in targets:
        vault_value = vault.get(key)
        env_value = os.environ.get(key)
        if env_value is None:
            differences[key] = {"vault": vault_value, "env": None, "status": "missing_in_env"}
        elif vault_value != env_value:
            differences[key] = {"vault": vault_value, "env": env_value, "status": "changed"}
    return differences
