"""Tests for envault.comment module."""

from __future__ import annotations

import pytest

from envault.comment import (
    set_comment,
    get_comment,
    remove_comment,
    list_comments,
)


class _FakeVault:
    def __init__(self, keys):
        self._keys = list(keys)

    def list_keys(self):
        return self._keys


@pytest.fixture()
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_set_and_get_comment(vault_path):
    vault = _FakeVault(["API_KEY"])
    set_comment(vault_path, "API_KEY", "Primary API key", vault=vault)
    assert get_comment(vault_path, "API_KEY") == "Primary API key"


def test_get_comment_missing_key_returns_none(vault_path):
    assert get_comment(vault_path, "NONEXISTENT") is None


def test_set_comment_missing_vault_key_raises(vault_path):
    vault = _FakeVault(["OTHER_KEY"])
    with pytest.raises(KeyError, match="API_KEY"):
        set_comment(vault_path, "API_KEY", "Some comment", vault=vault)


def test_set_comment_empty_text_raises(vault_path):
    vault = _FakeVault(["API_KEY"])
    with pytest.raises(ValueError, match="empty"):
        set_comment(vault_path, "API_KEY", "   ", vault=vault)


def test_set_comment_strips_whitespace(vault_path):
    vault = _FakeVault(["DB_PASS"])
    set_comment(vault_path, "DB_PASS", "  my note  ", vault=vault)
    assert get_comment(vault_path, "DB_PASS") == "my note"


def test_remove_comment_returns_true(vault_path):
    vault = _FakeVault(["TOKEN"])
    set_comment(vault_path, "TOKEN", "auth token", vault=vault)
    result = remove_comment(vault_path, "TOKEN")
    assert result is True
    assert get_comment(vault_path, "TOKEN") is None


def test_remove_comment_missing_returns_false(vault_path):
    assert remove_comment(vault_path, "GHOST") is False


def test_list_comments_empty(vault_path):
    assert list_comments(vault_path) == {}


def test_list_comments_multiple(vault_path):
    vault = _FakeVault(["KEY_A", "KEY_B"])
    set_comment(vault_path, "KEY_A", "first key", vault=vault)
    set_comment(vault_path, "KEY_B", "second key", vault=vault)
    result = list_comments(vault_path)
    assert result == {"KEY_A": "first key", "KEY_B": "second key"}


def test_set_comment_without_vault_validation(vault_path):
    """Passing vault=None skips key existence check."""
    set_comment(vault_path, "ANY_KEY", "free comment", vault=None)
    assert get_comment(vault_path, "ANY_KEY") == "free comment"
