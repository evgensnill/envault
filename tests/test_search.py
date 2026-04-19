"""Tests for envault.search module."""
from __future__ import annotations

import pytest

from envault.vault import Vault
from envault.search import search_keys, grep_values
from envault.rotation import record_rotation


PASSWORD = "test-pass"


def _make_vault(tmp_path, entries: dict) -> Vault:
    path = tmp_path / "vault.db"
    v = Vault(str(path), PASSWORD)
    for k, val in entries.items():
        v.set(k, val)
    return v


def test_search_no_pattern_returns_all(tmp_path):
    v = _make_vault(tmp_path, {"ALPHA": "1", "BETA": "2", "GAMMA": "3"})
    assert search_keys(v) == ["ALPHA", "BETA", "GAMMA"]


def test_search_glob_pattern(tmp_path):
    v = _make_vault(tmp_path, {"DB_HOST": "h", "DB_PORT": "p", "API_KEY": "k"})
    result = search_keys(v, "DB_*")
    assert result == ["DB_HOST", "DB_PORT"]


def test_search_regex_pattern(tmp_path):
    v = _make_vault(tmp_path, {"DB_HOST": "h", "DB_PORT": "p", "API_KEY": "k"})
    result = search_keys(v, r"^DB_", regex=True)
    assert result == ["DB_HOST", "DB_PORT"]


def test_search_no_match_returns_empty(tmp_path):
    v = _make_vault(tmp_path, {"ALPHA": "1"})
    assert search_keys(v, "NOPE_*") == []


def test_search_rotated_after_filters(tmp_path):
    v = _make_vault(tmp_path, {"KEY_A": "a", "KEY_B": "b"})
    record_rotation(v, "KEY_A")
    # KEY_A has a recent timestamp; KEY_B has none — both excluded when no rotation
    result = search_keys(v, rotated_after="2000-01-01T00:00:00")
    assert "KEY_A" in result
    assert "KEY_B" not in result


def test_search_rotated_before_excludes_recent(tmp_path):
    v = _make_vault(tmp_path, {"KEY_A": "a"})
    record_rotation(v, "KEY_A")
    # Rotated just now, so rotated_before a past date should exclude it
    result = search_keys(v, rotated_before="2000-01-01T00:00:00")
    assert result == []


def test_grep_values_glob(tmp_path):
    v = _make_vault(tmp_path, {"A": "hello_world", "B": "hello_there", "C": "bye"})
    result = grep_values(v, "hello_*")
    assert result == ["A", "B"]


def test_grep_values_regex(tmp_path):
    v = _make_vault(tmp_path, {"A": "abc123", "B": "xyz", "C": "def456"})
    result = grep_values(v, r"\d+", regex=True)
    assert result == ["A", "C"]


def test_grep_values_no_match(tmp_path):
    v = _make_vault(tmp_path, {"A": "foo", "B": "bar"})
    assert grep_values(v, "zzz*") == []
