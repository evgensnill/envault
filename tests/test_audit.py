"""Tests for envault.audit module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.audit import record_event, read_events, filter_events


@pytest.fixture()
def vault_path(tmp_path: Path) -> str:
    return str(tmp_path / "test.vault")


def test_record_creates_log_file(vault_path: str, tmp_path: Path) -> None:
    record_event(vault_path, action="set", key="API_KEY")
    log = tmp_path / ".envault_audit.log"
    assert log.exists()


def test_record_event_fields(vault_path: str, tmp_path: Path) -> None:
    record_event(vault_path, action="get", key="DB_PASS", actor="alice")
    log = tmp_path / ".envault_audit.log"
    events = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
    assert len(events) == 1
    ev = events[0]
    assert ev["action"] == "get"
    assert ev["key"] == "DB_PASS"
    assert ev["actor"] == "alice"
    assert "timestamp" in ev


def test_multiple_events_appended(vault_path: str) -> None:
    record_event(vault_path, action="set", key="A")
    record_event(vault_path, action="set", key="B")
    record_event(vault_path, action="delete", key="A")
    events = read_events(vault_path)
    assert len(events) == 3
    assert events[0]["key"] == "A"
    assert events[2]["action"] == "delete"


def test_read_events_empty_when_no_log(vault_path: str) -> None:
    events = read_events(vault_path)
    assert events == []


def test_filter_by_action(vault_path: str) -> None:
    record_event(vault_path, action="set", key="X")
    record_event(vault_path, action="get", key="X")
    record_event(vault_path, action="set", key="Y")
    sets = filter_events(vault_path, action="set")
    assert all(e["action"] == "set" for e in sets)
    assert len(sets) == 2


def test_filter_by_key(vault_path: str) -> None:
    record_event(vault_path, action="set", key="SECRET")
    record_event(vault_path, action="rotate", key="SECRET")
    record_event(vault_path, action="set", key="OTHER")
    key_events = filter_events(vault_path, key="SECRET")
    assert len(key_events) == 2
    assert all(e["key"] == "SECRET" for e in key_events)


def test_filter_by_action_and_key(vault_path: str) -> None:
    record_event(vault_path, action="set", key="K1")
    record_event(vault_path, action="get", key="K1")
    record_event(vault_path, action="set", key="K2")
    result = filter_events(vault_path, action="set", key="K1")
    assert len(result) == 1
    assert result[0]["action"] == "set"
    assert result[0]["key"] == "K1"


def test_extra_fields_recorded(vault_path: str) -> None:
    record_event(vault_path, action="export", extra={"format": "dotenv"})
    events = read_events(vault_path)
    assert events[0]["format"] == "dotenv"
