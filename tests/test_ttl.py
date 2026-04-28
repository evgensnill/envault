"""Tests for envault.ttl."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault import ttl as ttl_mod


@pytest.fixture()
def vault_path(tmp_path: Path) -> str:
    p = tmp_path / "vault.db"
    p.write_text("{}")
    return str(p)


# ---------------------------------------------------------------------------
# set / get
# ---------------------------------------------------------------------------

def test_set_and_get_ttl(vault_path):
    ttl_mod.set_ttl(vault_path, "API_KEY", 3600)
    meta = ttl_mod.get_ttl(vault_path, "API_KEY")
    assert meta is not None
    assert meta["ttl_seconds"] == 3600
    assert meta["expires_at"] > time.time()


def test_get_ttl_missing_key_returns_none(vault_path):
    assert ttl_mod.get_ttl(vault_path, "MISSING") is None


def test_set_ttl_overwrites_existing(vault_path):
    """Re-setting a TTL for the same key should update the record."""
    ttl_mod.set_ttl(vault_path, "API_KEY", 3600)
    ttl_mod.set_ttl(vault_path, "API_KEY", 7200)
    meta = ttl_mod.get_ttl(vault_path, "API_KEY")
    assert meta is not None
    assert meta["ttl_seconds"] == 7200


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------

def test_remove_ttl_returns_true(vault_path):
    ttl_mod.set_ttl(vault_path, "DB_PASS", 60)
    assert ttl_mod.remove_ttl(vault_path, "DB_PASS") is True
    assert ttl_mod.get_ttl(vault_path, "DB_PASS") is None


def test_remove_ttl_missing_returns_false(vault_path):
    assert ttl_mod.remove_ttl(vault_path, "NOPE") is False


# ---------------------------------------------------------------------------
# is_expired
# ---------------------------------------------------------------------------

def test_not_expired_for_future_ttl(vault_path):
    ttl_mod.set_ttl(vault_path, "TOKEN", 9999)
    assert ttl_mod.is_expired(vault_path, "TOKEN") is False


def test_expired_for_past_ttl(vault_path, monkeypatch):
    ttl_mod.set_ttl(vault_path, "TOKEN", 1)
    # wind time forward
    monkeypatch.setattr(ttl_mod, "time", type("_T", (), {"time": staticmethod(lambda: time.time() + 10)})())
    assert ttl_mod.is_expired(vault_path, "TOKEN") is True


def test_is_expired_no_ttl_returns_false(vault_path):
    assert ttl_mod.is_expired(vault_path, "GHOST") is False


# ---------------------------------------------------------------------------
# expired_keys / list_ttls
# ---------------------------------------------------------------------------

def test_expired_keys_filters_correctly(vault_path, monkeypatch):
    ttl_mod.set_ttl(vault_path, "OLD", 1)
    ttl_mod.set_ttl(vault_path, "NEW", 9999)
    monkeypatch.setattr(ttl_mod, "time", type("_T", (), {"time": staticmethod(lambda: time.time() + 10)})())
    result = ttl_mod.expired_keys(vault_path, ["OLD", "NEW", "NONE"])
    assert "OLD" in result
    assert "NEW" not in result
    assert "NONE" not in result


def test_list_ttls_returns_all_records(vault_path):
    ttl_mod.set_ttl(vault_path, "A", 100)
    ttl_mod.set_ttl(vault_path, "B", 200)
    records = ttl_mod.list_ttls(vault_path)
    assert set(records.keys()) == {"A", "B"}


def test_list_ttls_empty_vault(vault_path):
    """list_ttls should return an empty dict when no TTLs have been set."""
    records = ttl_mod.list_ttls(vault_path)
    assert records == {}
