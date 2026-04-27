"""Webhook notification support for envault events."""
from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

VALID_EVENTS = {"set", "rotate", "delete", "import", "restore", "expire"}


def _webhooks_path(vault_path: str) -> Path:
    return Path(vault_path).with_suffix(".webhooks.json")


def _load(vault_path: str) -> dict:
    p = _webhooks_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(vault_path: str, data: dict) -> None:
    _webhooks_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class WebhookEntry:
    url: str
    events: list[str]
    secret: str = ""
    enabled: bool = True
    extra: dict = field(default_factory=dict)


def add_webhook(vault_path: str, name: str, url: str, events: list[str], secret: str = "") -> WebhookEntry:
    if not events:
        raise ValueError("At least one event must be specified.")
    invalid = set(events) - VALID_EVENTS
    if invalid:
        raise ValueError(f"Invalid events: {', '.join(sorted(invalid))}. Valid: {', '.join(sorted(VALID_EVENTS))}")
    data = _load(vault_path)
    entry = {"url": url, "events": events, "secret": secret, "enabled": True}
    data[name] = entry
    _save(vault_path, data)
    return WebhookEntry(**entry)


def remove_webhook(vault_path: str, name: str) -> bool:
    data = _load(vault_path)
    if name not in data:
        return False
    del data[name]
    _save(vault_path, data)
    return True


def list_webhooks(vault_path: str) -> dict[str, WebhookEntry]:
    data = _load(vault_path)
    return {name: WebhookEntry(**entry) for name, entry in data.items()}


def dispatch_webhook(entry: WebhookEntry, event: str, payload: dict[str, Any]) -> bool:
    """Send an HTTP POST to the webhook URL. Returns True on success."""
    if not entry.enabled or event not in entry.events:
        return False
    body = json.dumps({"event": event, "timestamp": time.time(), "payload": payload}).encode()
    headers = {"Content-Type": "application/json"}
    if entry.secret:
        headers["X-Envault-Secret"] = entry.secret
    req = urllib.request.Request(entry.url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5):
            return True
    except urllib.error.URLError:
        return False


def fire_event(vault_path: str, event: str, payload: dict[str, Any]) -> dict[str, bool]:
    """Dispatch event to all matching webhooks. Returns {name: success}."""
    results = {}
    for name, entry in list_webhooks(vault_path).items():
        results[name] = dispatch_webhook(entry, event, payload)
    return results
