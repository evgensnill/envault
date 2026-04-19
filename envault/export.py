"""Export vault secrets to various formats."""
from __future__ import annotations
import json
from typing import Literal

from envault.vault import Vault

ExportFormat = Literal["dotenv", "json", "shell"]


def export_vault(vault: Vault, fmt: ExportFormat = "dotenv") -> str:
    """Export all secrets from *vault* as a string in the requested format."""
    keys = vault.list_keys()
    secrets = {k: vault.get(k) for k in keys}

    if fmt == "json":
        return _to_json(secrets)
    if fmt == "shell":
        return _to_shell(secrets)
    return _to_dotenv(secrets)


def _to_dotenv(secrets: dict[str, str]) -> str:
    lines = []
    for key, value in sorted(secrets.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def _to_json(secrets: dict[str, str]) -> str:
    return json.dumps(secrets, indent=2, sort_keys=True) + "\n"


def _to_shell(secrets: dict[str, str]) -> str:
    lines = []
    for key, value in sorted(secrets.items()):
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")
