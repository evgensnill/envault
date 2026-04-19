"""Template rendering: substitute vault secrets into template strings/files."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from envault.vault import Vault

_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_string(template: str, vault: Vault) -> tuple[str, list[str]]:
    """Replace {{KEY}} placeholders with vault values.

    Returns (rendered_text, list_of_missing_keys).
    """
    missing: list[str] = []

    def _replace(m: re.Match) -> str:
        key = m.group(1)
        try:
            return vault.get(key)
        except KeyError:
            missing.append(key)
            return m.group(0)  # leave placeholder intact

    rendered = _PLACEHOLDER.sub(_replace, template)
    return rendered, missing


def render_file(
    src: Path,
    vault: Vault,
    dest: Optional[Path] = None,
) -> tuple[str, list[str]]:
    """Read *src*, render placeholders, optionally write to *dest*.

    Returns (rendered_text, list_of_missing_keys).
    """
    text = src.read_text(encoding="utf-8")
    rendered, missing = render_string(text, vault)
    if dest is not None:
        dest.write_text(rendered, encoding="utf-8")
    return rendered, missing
