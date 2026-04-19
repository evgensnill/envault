"""Audit log for envault — records vault operations to a local log file."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_AUDIT_LOG = ".envault_audit.log"


def _log_path(vault_path: str) -> Path:
    base = Path(vault_path).parent
    return base / DEFAULT_AUDIT_LOG


def record_event(
    vault_path: str,
    action: str,
    key: str | None = None,
    actor: str | None = None,
    extra: Dict[str, Any] | None = None,
) -> None:
    """Append a structured audit event to the log file."""
    event: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
    }
    if key is not None:
        event["key"] = key
    event["actor"] = actor or os.environ.get("USER", "unknown")
    if extra:
        event.update(extra)

    log_file = _log_path(vault_path)
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def read_events(vault_path: str) -> List[Dict[str, Any]]:
    """Return all audit events from the log file, oldest first."""
    log_file = _log_path(vault_path)
    if not log_file.exists():
        return []
    events: List[Dict[str, Any]] = []
    with log_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def filter_events(
    vault_path: str,
    action: str | None = None,
    key: str | None = None,
) -> List[Dict[str, Any]]:
    """Return events optionally filtered by action and/or key."""
    events = read_events(vault_path)
    if action:
        events = [e for e in events if e.get("action") == action]
    if key:
        events = [e for e in events if e.get("key") == key]
    return events
