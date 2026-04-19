"""Compare vault contents against the current process environment."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envault.vault import Vault


@dataclass
class EnvCheckResult:
    key: str
    status: str   # 'ok' | 'missing' | 'mismatch'
    vault_value: str | None = None
    env_value: str | None = None


def check_env(vault: Vault, *, keys: list[str] | None = None) -> List[EnvCheckResult]:
    """Check whether env vars match the vault.

    Args:
        vault: Loaded Vault instance.
        keys: Subset of keys to check; defaults to all vault keys.

    Returns:
        List of EnvCheckResult, one per checked key.
    """
    import os

    target_keys = keys if keys is not None else vault.list_keys()
    results: List[EnvCheckResult] = []

    for key in target_keys:
        vault_val = vault.get(key)
        env_val = os.environ.get(key)

        if env_val is None:
            results.append(EnvCheckResult(key=key, status="missing",
                                          vault_value=vault_val, env_value=None))
        elif env_val != vault_val:
            results.append(EnvCheckResult(key=key, status="mismatch",
                                          vault_value=vault_val, env_value=env_val))
        else:
            results.append(EnvCheckResult(key=key, status="ok",
                                          vault_value=vault_val, env_value=env_val))

    return results
