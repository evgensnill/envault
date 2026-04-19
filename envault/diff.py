"""Vault diff: compare two vault snapshots or vault vs env file."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional

from envault.vault import Vault


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added' | 'removed' | 'changed' | 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


def diff_vaults(
    vault_a: Vault,
    vault_b: Vault,
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare two Vault instances and return a list of DiffEntry."""
    keys_a = set(vault_a.list_keys())
    keys_b = set(vault_b.list_keys())
    results: List[DiffEntry] = []

    for key in sorted(keys_a | keys_b):
        if key in keys_a and key not in keys_b:
            results.append(DiffEntry(key=key, status="removed", old_value=vault_a.get(key)))
        elif key in keys_b and key not in keys_a:
            results.append(DiffEntry(key=key, status="added", new_value=vault_b.get(key)))
        else:
            val_a = vault_a.get(key)
            val_b = vault_b.get(key)
            if val_a != val_b:
                results.append(DiffEntry(key=key, status="changed", old_value=val_a, new_value=val_b))
            elif show_unchanged:
                results.append(DiffEntry(key=key, status="unchanged", old_value=val_a, new_value=val_b))

    return results


def diff_vault_vs_env(vault: Vault, env_dict: Dict[str, str], show_unchanged: bool = False) -> List[DiffEntry]:
    """Compare a vault against a plain dict (e.g. parsed from .env or os.environ)."""
    keys_vault = set(vault.list_keys())
    keys_env = set(env_dict.keys())
    results: List[DiffEntry] = []

    for key in sorted(keys_vault | keys_env):
        if key in keys_vault and key not in keys_env:
            results.append(DiffEntry(key=key, status="removed", old_value=vault.get(key)))
        elif key in keys_env and key not in keys_vault:
            results.append(DiffEntry(key=key, status="added", new_value=env_dict[key]))
        else:
            val_v = vault.get(key)
            val_e = env_dict[key]
            if val_v != val_e:
                results.append(DiffEntry(key=key, status="changed", old_value=val_v, new_value=val_e))
            elif show_unchanged:
                results.append(DiffEntry(key=key, status="unchanged", old_value=val_v, new_value=val_e))

    return results
