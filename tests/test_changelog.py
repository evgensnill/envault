"""Tests for envault.changelog."""
import pytest
from pathlib import Path
from envault.changelog import record_change, get_history, clear_history


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_record_creates_changelog_file(vault_path, tmp_path):
    record_change(vault_path, "API_KEY", "set")
    log = tmp_path / "test.changelog.json"
    assert log.exists()


def test_record_entry_fields(vault_path):
    record_change(vault_path, "DB_PASS", "set", actor="alice", note="initial")
    entries = get_history(vault_path)
    assert len(entries) == 1
    e = entries[0]
    assert e["key"] == "DB_PASS"
    assert e["action"] == "set"
    assert e["actor"] == "alice"
    assert e["note"] == "initial"
    assert "timestamp" in e


def test_multiple_entries_appended(vault_path):
    record_change(vault_path, "KEY1", "set")
    record_change(vault_path, "KEY1", "rotate")
    record_change(vault_path, "KEY1", "delete")
    assert len(get_history(vault_path)) == 3


def test_filter_by_key(vault_path):
    record_change(vault_path, "A", "set")
    record_change(vault_path, "B", "set")
    record_change(vault_path, "A", "rotate")
    result = get_history(vault_path, key="A")
    assert all(e["key"] == "A" for e in result)
    assert len(result) == 2


def test_filter_by_action(vault_path):
    record_change(vault_path, "X", "set")
    record_change(vault_path, "X", "rotate")
    record_change(vault_path, "Y", "rotate")
    result = get_history(vault_path, action="rotate")
    assert all(e["action"] == "rotate" for e in result)
    assert len(result) == 2


def test_limit(vault_path):
    for i in range(10):
        record_change(vault_path, f"KEY{i}", "set")
    result = get_history(vault_path, limit=3)
    assert len(result) == 3
    assert result[-1]["key"] == "KEY9"


def test_invalid_action_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid action"):
        record_change(vault_path, "KEY", "update")


def test_clear_history(vault_path):
    record_change(vault_path, "KEY", "set")
    clear_history(vault_path)
    assert get_history(vault_path) == []


def test_get_history_no_file_returns_empty(vault_path):
    assert get_history(vault_path) == []
