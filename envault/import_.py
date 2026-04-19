"""Import secrets into a vault from external formats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

from envault.vault import Vault


def _parse_dotenv(text: str) -> Dict[str, str]:
    """Parse a .env file into a key/value dict, skipping comments and blanks."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip optional surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def _parse_json(text: str) -> Dict[str, str]:
    """Parse a flat JSON object into a key/value dict."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON import requires a top-level object.")
    return {str(k): str(v) for k, v in data.items()}


def import_vault(
    vault: Vault,
    source: Path,
    fmt: str = "dotenv",
    overwrite: bool = False,
) -> Tuple[int, int]:
    """Import key/value pairs from *source* into *vault*.

    Returns (imported, skipped) counts.
    """
    text = source.read_text(encoding="utf-8")

    parsers = {
        "dotenv": _parse_dotenv,
        "json": _parse_json,
    }
    if fmt not in parsers:
        raise ValueError(f"Unsupported import format: {fmt!r}. Choose from {list(parsers)}.")

    pairs = parsers[fmt](text)

    imported = 0
    skipped = 0
    for key, value in pairs.items():
        if not overwrite and vault.has(key):
            skipped += 1
            continue
        vault.set(key, value)
        imported += 1

    if imported:
        vault.save()

    return imported, skipped
