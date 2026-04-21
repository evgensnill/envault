"""Tests for envault.pin — key pinning feature."""

from __future__ import annotations

import pytest

from envault.pin import (
    assert_not_pinned,
    is_pinned,
    list_pins,
    pin_key,
    unpin_key,
)


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "vault.env")


def test_pin_key_marks_key(vault_path):
    pin_key(vault_path, "SECRET_KEY", "stable prod value")
    assert is_pinned(vault_path, "SECRET_KEY")


def test_unpin_key_removes_pin(vault_path):
    pin_key(vault_path, "API_TOKEN")
    assert unpin_key(vault_path, "API_TOKEN") is True
    assert not is_pinned(vault_path, "API_TOKEN")


def test_unpin_missing_key_returns_false(vault_path):
    assert unpin_key(vault_path, "NONEXISTENT") is False


def test_is_pinned_returns_false_for_unknown_key(vault_path):
    assert not is_pinned(vault_path, "UNKNOWN_KEY")


def test_list_pins_empty(vault_path):
    assert list_pins(vault_path) == []


def test_list_pins_returns_all(vault_path):
    pin_key(vault_path, "KEY_A", "reason A")
    pin_key(vault_path, "KEY_B", "reason B")
    pins = list_pins(vault_path)
    keys = {p["key"] for p in pins}
    assert keys == {"KEY_A", "KEY_B"}
    reasons = {p["key"]: p["reason"] for p in pins}
    assert reasons["KEY_A"] == "reason A"
    assert reasons["KEY_B"] == "reason B"


def test_pin_idempotent_updates_reason(vault_path):
    pin_key(vault_path, "DB_PASS", "first reason")
    pin_key(vault_path, "DB_PASS", "updated reason")
    pins = {p["key"]: p["reason"] for p in list_pins(vault_path)}
    assert pins["DB_PASS"] == "updated reason"


def test_assert_not_pinned_raises_when_pinned(vault_path):
    pin_key(vault_path, "LOCKED_KEY", "do not touch")
    with pytest.raises(ValueError, match="LOCKED_KEY"):
        assert_not_pinned(vault_path, "LOCKED_KEY")


def test_assert_not_pinned_includes_reason_in_message(vault_path):
    pin_key(vault_path, "LOCKED_KEY", "critical secret")
    with pytest.raises(ValueError, match="critical secret"):
        assert_not_pinned(vault_path, "LOCKED_KEY")


def test_assert_not_pinned_passes_for_free_key(vault_path):
    # Should not raise
    assert_not_pinned(vault_path, "FREE_KEY")


def test_pins_persisted_across_calls(vault_path):
    pin_key(vault_path, "PERSIST_ME", "persisted")
    # Re-load by calling list_pins again (reads from disk)
    result = list_pins(vault_path)
    assert any(p["key"] == "PERSIST_ME" for p in result)
