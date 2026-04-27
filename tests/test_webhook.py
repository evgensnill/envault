"""Tests for envault.webhook."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from envault import webhook as wh


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "vault.env"
    p.write_text("{}")
    return str(p)


def test_add_webhook_and_list(vault_path):
    entry = wh.add_webhook(vault_path, "slack", "https://hooks.example.com/slack", ["set", "rotate"])
    assert entry.url == "https://hooks.example.com/slack"
    assert set(entry.events) == {"set", "rotate"}
    assert entry.enabled is True

    entries = wh.list_webhooks(vault_path)
    assert "slack" in entries


def test_add_webhook_invalid_event_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid events"):
        wh.add_webhook(vault_path, "bad", "https://example.com", ["nonexistent"])


def test_add_webhook_no_events_raises(vault_path):
    with pytest.raises(ValueError, match="At least one event"):
        wh.add_webhook(vault_path, "bad", "https://example.com", [])


def test_remove_webhook_returns_true(vault_path):
    wh.add_webhook(vault_path, "hook1", "https://example.com", ["set"])
    assert wh.remove_webhook(vault_path, "hook1") is True
    assert "hook1" not in wh.list_webhooks(vault_path)


def test_remove_missing_webhook_returns_false(vault_path):
    assert wh.remove_webhook(vault_path, "ghost") is False


def test_list_webhooks_empty_when_no_file(vault_path):
    entries = wh.list_webhooks(vault_path)
    assert entries == {}


def test_dispatch_webhook_skips_wrong_event(vault_path):
    entry = wh.WebhookEntry(url="https://example.com", events=["rotate"])
    result = wh.dispatch_webhook(entry, "set", {})
    assert result is False


def test_dispatch_webhook_skips_disabled(vault_path):
    entry = wh.WebhookEntry(url="https://example.com", events=["set"], enabled=False)
    result = wh.dispatch_webhook(entry, "set", {})
    assert result is False


def test_dispatch_webhook_sends_request(vault_path):
    entry = wh.WebhookEntry(url="https://example.com/hook", events=["set"], secret="mysecret")
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_ctx) as mock_open:
        result = wh.dispatch_webhook(entry, "set", {"key": "FOO"})
    assert result is True
    assert mock_open.called


def test_dispatch_webhook_returns_false_on_error(vault_path):
    import urllib.error
    entry = wh.WebhookEntry(url="https://invalid.example.com", events=["set"])
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        result = wh.dispatch_webhook(entry, "set", {})
    assert result is False


def test_fire_event_dispatches_to_all(vault_path):
    wh.add_webhook(vault_path, "h1", "https://a.example.com", ["set"])
    wh.add_webhook(vault_path, "h2", "https://b.example.com", ["rotate"])
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_ctx):
        results = wh.fire_event(vault_path, "set", {"key": "BAR"})
    assert results["h1"] is True
    assert results["h2"] is False  # wrong event


def test_webhooks_file_is_valid_json(vault_path):
    wh.add_webhook(vault_path, "test", "https://example.com", ["delete"])
    p = wh._webhooks_path(vault_path)
    data = json.loads(p.read_text())
    assert "test" in data
    assert data["test"]["events"] == ["delete"]
