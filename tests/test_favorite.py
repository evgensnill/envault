"""Tests for envault.favorite."""
from __future__ import annotations

import pytest

from envault.favorite import (
    add_favorite,
    clear_favorites,
    is_favorite,
    list_favorites,
    remove_favorite,
)


class _FakeVault:
    def __init__(self, keys):
        self._keys = keys

    def list_keys(self):
        return list(self._keys)


def _make_vault(tmp_path, keys=("API_KEY", "DB_PASS", "SECRET")):
    vp = str(tmp_path / "vault.env")
    return vp, _FakeVault(keys)


def test_add_and_is_favorite(tmp_path):
    vp, vault = _make_vault(tmp_path)
    add_favorite(vp, "API_KEY", vault)
    assert is_favorite(vp, "API_KEY") is True


def test_is_favorite_returns_false_for_unknown(tmp_path):
    vp, vault = _make_vault(tmp_path)
    assert is_favorite(vp, "API_KEY") is False


def test_add_missing_key_raises(tmp_path):
    vp, vault = _make_vault(tmp_path)
    with pytest.raises(KeyError, match="NOT_EXIST"):
        add_favorite(vp, "NOT_EXIST", vault)


def test_add_duplicate_is_idempotent(tmp_path):
    vp, vault = _make_vault(tmp_path)
    add_favorite(vp, "API_KEY", vault)
    add_favorite(vp, "API_KEY", vault)
    assert list_favorites(vp).count("API_KEY") == 1


def test_list_favorites_returns_all(tmp_path):
    vp, vault = _make_vault(tmp_path)
    add_favorite(vp, "API_KEY", vault)
    add_favorite(vp, "DB_PASS", vault)
    favs = list_favorites(vp)
    assert "API_KEY" in favs
    assert "DB_PASS" in favs
    assert len(favs) == 2


def test_list_favorites_empty_when_no_file(tmp_path):
    vp, _ = _make_vault(tmp_path)
    assert list_favorites(vp) == []


def test_remove_favorite_returns_true(tmp_path):
    vp, vault = _make_vault(tmp_path)
    add_favorite(vp, "SECRET", vault)
    result = remove_favorite(vp, "SECRET")
    assert result is True
    assert is_favorite(vp, "SECRET") is False


def test_remove_missing_favorite_returns_false(tmp_path):
    vp, _ = _make_vault(tmp_path)
    assert remove_favorite(vp, "NOPE") is False


def test_clear_favorites_removes_all(tmp_path):
    vp, vault = _make_vault(tmp_path)
    add_favorite(vp, "API_KEY", vault)
    add_favorite(vp, "DB_PASS", vault)
    count = clear_favorites(vp)
    assert count == 2
    assert list_favorites(vp) == []


def test_clear_favorites_empty_vault_returns_zero(tmp_path):
    vp, _ = _make_vault(tmp_path)
    assert clear_favorites(vp) == 0
