"""Vault locking: prevent concurrent modifications by placing a lock file."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional

_LOCK_SUFFIX = ".lock"
_DEFAULT_TIMEOUT = 10  # seconds
_STALE_AFTER = 60  # seconds before a lock is considered stale


def _lock_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(_LOCK_SUFFIX)


def acquire_lock(vault_path: Path, timeout: float = _DEFAULT_TIMEOUT) -> None:
    """Acquire a lock for *vault_path*.

    Raises RuntimeError if the lock cannot be acquired within *timeout* seconds.
    Stale locks (older than _STALE_AFTER seconds) are removed automatically.
    """
    lock = _lock_path(vault_path)
    deadline = time.monotonic() + timeout
    while True:
        if lock.exists():
            try:
                data = json.loads(lock.read_text())
                age = time.time() - data.get("acquired_at", 0)
                if age > _STALE_AFTER:
                    lock.unlink(missing_ok=True)
            except (json.JSONDecodeError, OSError):
                lock.unlink(missing_ok=True)

        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                json.dump({"pid": os.getpid(), "acquired_at": time.time()}, f)
            return
        except FileExistsError:
            pass

        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"Could not acquire lock for '{vault_path}' within {timeout}s. "
                "Another envault process may be running."
            )
        time.sleep(0.1)


def release_lock(vault_path: Path) -> None:
    """Release the lock for *vault_path* (no-op if not locked)."""
    _lock_path(vault_path).unlink(missing_ok=True)


def is_locked(vault_path: Path) -> bool:
    """Return True if a (non-stale) lock exists for *vault_path*."""
    lock = _lock_path(vault_path)
    if not lock.exists():
        return False
    try:
        data = json.loads(lock.read_text())
        age = time.time() - data.get("acquired_at", 0)
        return age <= _STALE_AFTER
    except (json.JSONDecodeError, OSError):
        return False


def lock_info(vault_path: Path) -> Optional[dict]:
    """Return lock metadata dict or None if not locked."""
    lock = _lock_path(vault_path)
    if not lock.exists():
        return None
    try:
        return json.loads(lock.read_text())
    except (json.JSONDecodeError, OSError):
        return None
