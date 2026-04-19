"""Pre/post hooks for vault operations."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Optional

HOOKS_FILE = ".envault-hooks.json"

_VALID_EVENTS = {"pre-set", "post-set", "pre-delete", "post-delete", "post-rotate"}


def _hooks_path(vault_path: Path) -> Path:
    return vault_path.parent / HOOKS_FILE


def load_hooks(vault_path: Path) -> dict:
    p = _hooks_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_hooks(vault_path: Path, hooks: dict) -> None:
    p = _hooks_path(vault_path)
    p.write_text(json.dumps(hooks, indent=2))


def add_hook(vault_path: Path, event: str, command: str) -> None:
    if event not in _VALID_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid: {sorted(_VALID_EVENTS)}")
    hooks = load_hooks(vault_path)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    save_hooks(vault_path, hooks)


def remove_hook(vault_path: Path, event: str, command: str) -> bool:
    hooks = load_hooks(vault_path)
    cmds: List[str] = hooks.get(event, [])
    if command not in cmds:
        return False
    cmds.remove(command)
    hooks[event] = cmds
    save_hooks(vault_path, hooks)
    return True


def run_hooks(vault_path: Path, event: str, env: Optional[dict] = None) -> List[str]:
    """Run all commands registered for *event*. Returns list of outputs."""
    hooks = load_hooks(vault_path)
    outputs = []
    for cmd in hooks.get(event, []):
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, env=env
        )
        outputs.append(result.stdout.strip())
    return outputs
