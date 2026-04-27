"""Quota management: limit the number of keys stored in a vault."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_QUOTA_FILE = ".envault_quota.json"


def _quota_path(vault_path: str) -> Path:
    return Path(vault_path).parent / _QUOTA_FILE


def _load(vault_path: str) -> dict:
    p = _quota_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _quota_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class QuotaInfo:
    limit: int
    current: int

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.current)

    @property
    def exceeded(self) -> bool:
        return self.current > self.limit


class QuotaExceededError(Exception):
    """Raised when adding a key would exceed the vault quota."""


def set_quota(vault_path: str, limit: int) -> None:
    """Set the maximum number of keys allowed in the vault."""
    if limit < 1:
        raise ValueError("Quota limit must be at least 1.")
    data = _load(vault_path)
    data["limit"] = limit
    _save(vault_path, data)


def get_quota(vault_path: str) -> Optional[int]:
    """Return the configured quota limit, or None if not set."""
    return _load(vault_path).get("limit")


def remove_quota(vault_path: str) -> bool:
    """Remove the quota limit. Returns True if a limit existed."""
    data = _load(vault_path)
    if "limit" not in data:
        return False
    del data["limit"]
    _save(vault_path, data)
    return True


def check_quota(vault_path: str, vault) -> QuotaInfo:
    """Check current usage against the quota.

    Args:
        vault_path: Path to the vault file.
        vault: Vault instance with a list_keys() method.

    Returns:
        QuotaInfo with limit and current count.

    Raises:
        QuotaExceededError if the vault already exceeds its limit.
    """
    limit = get_quota(vault_path)
    if limit is None:
        raise ValueError("No quota configured for this vault.")
    current = len(vault.list_keys())
    info = QuotaInfo(limit=limit, current=current)
    if info.exceeded:
        raise QuotaExceededError(
            f"Vault exceeds quota: {current} keys stored, limit is {limit}."
        )
    return info


def enforce_quota(vault_path: str, vault) -> None:
    """Raise QuotaExceededError if adding one more key would exceed the quota."""
    limit = get_quota(vault_path)
    if limit is None:
        return
    current = len(vault.list_keys())
    if current >= limit:
        raise QuotaExceededError(
            f"Cannot add key: vault has {current}/{limit} keys (quota reached)."
        )
