"""envault.redact — utilities for redacting sensitive values in output.

Provides masking helpers used when displaying vault contents in logs,
CLI output, or exported reports so raw secrets are never accidentally
exposed in plain text.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MASK = "****"
DEFAULT_VISIBLE_CHARS = 4  # chars revealed at the end (e.g. "…b3f9")

# Patterns that suggest a key holds a sensitive value even if not explicitly
# flagged.  Matched case-insensitively against the key name.
_SENSITIVE_PATTERNS: List[str] = [
    r"secret",
    r"password",
    r"passwd",
    r"token",
    r"api[_-]?key",
    r"private[_-]?key",
    r"auth",
    r"credential",
    r"access[_-]?key",
]

_SENSITIVE_RE = re.compile(
    "|".join(_SENSITIVE_PATTERNS),
    re.IGNORECASE,
)

# Path to the per-vault redaction config (list of explicitly redacted keys).
def _redact_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.stem + ".redact.json")


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

import json


def _load(vault_path: Path) -> Dict[str, bool]:
    """Return mapping of key -> True for explicitly redacted keys."""
    p = _redact_path(vault_path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(vault_path: Path, store: Dict[str, bool]) -> None:
    p = _redact_path(vault_path)
    p.write_text(json.dumps(store, indent=2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def mark_redacted(vault_path: Path, key: str) -> None:
    """Explicitly mark *key* as redacted in the vault's redaction config."""
    store = _load(vault_path)
    store[key] = True
    _save(vault_path, store)


def unmark_redacted(vault_path: Path, key: str) -> bool:
    """Remove an explicit redaction mark.  Returns True if mark existed."""
    store = _load(vault_path)
    if key not in store:
        return False
    del store[key]
    _save(vault_path, store)
    return True


def is_redacted(vault_path: Path, key: str) -> bool:
    """Return True if *key* is explicitly marked as redacted."""
    return _load(vault_path).get(key, False)


def list_redacted(vault_path: Path) -> List[str]:
    """Return all keys that are explicitly marked as redacted."""
    return sorted(k for k, v in _load(vault_path).items() if v)


def is_sensitive_key(key: str) -> bool:
    """Heuristically decide whether *key* looks like it holds a secret.

    This does **not** require the vault path — it inspects only the key name.
    """
    return bool(_SENSITIVE_RE.search(key))


def mask_value(
    value: str,
    *,
    visible_chars: int = DEFAULT_VISIBLE_CHARS,
    mask: str = DEFAULT_MASK,
) -> str:
    """Return a masked representation of *value*.

    The last *visible_chars* characters are preserved so users can do a
    quick sanity-check without revealing the full secret::

        >>> mask_value("supersecrettoken")
        '****oken'
    """
    if not value:
        return mask
    if visible_chars <= 0 or len(value) <= visible_chars:
        return mask
    return mask + value[-visible_chars:]


def redact_dict(
    vault_path: Path,
    data: Dict[str, str],
    *,
    auto_detect: bool = True,
    visible_chars: int = DEFAULT_VISIBLE_CHARS,
    mask: str = DEFAULT_MASK,
) -> Dict[str, str]:
    """Return a copy of *data* with sensitive values masked.

    A key is masked when any of the following is true:

    * It is explicitly marked in the vault's redaction config.
    * *auto_detect* is True and :func:`is_sensitive_key` returns True.
    """
    explicit = set(list_redacted(vault_path))
    result: Dict[str, str] = {}
    for key, value in data.items():
        if key in explicit or (auto_detect and is_sensitive_key(key)):
            result[key] = mask_value(value, visible_chars=visible_chars, mask=mask)
        else:
            result[key] = value
    return result
