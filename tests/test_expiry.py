"""Tests for envault.expiry module."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.expiry import (
    expired_keys,
    get_expiry,
    is_expired,
    list_expiries,
    remove_expiry,
    set_expiry,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> str:
    return str(tmp_path / "test.vault")


def _future(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


def _past(seconds: int = 3600) -> datetime:
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


def test_set_and_get_expiry(vault_path: str) -> None:
    expiry = _future()
    set_expiry(vault_path, "MY_KEY", expiry)
    result = get_expiry(vault_path, "MY_KEY")
    assert result is not None
    assert abs((result - expiry).total_seconds()) < 1


def test_get_expiry_missing_key_returns_none(vault_path: str) -> None:
    assert get_expiry(vault_path, "MISSING") is None


def test_remove_expiry_returns_true(vault_path: str) -> None:
    set_expiry(vault_path, "KEY", _future())
    assert remove_expiry(vault_path, "KEY") is True
    assert get_expiry(vault_path, "KEY") is None


def test_remove_expiry_missing_returns_false(vault_path: str) -> None:
    assert remove_expiry(vault_path, "GHOST") is False


def test_is_expired_future_key(vault_path: str) -> None:
    set_expiry(vault_path, "FUTURE_KEY", _future())
    assert is_expired(vault_path, "FUTURE_KEY") is False


def test_is_expired_past_key(vault_path: str) -> None:
    set_expiry(vault_path, "OLD_KEY", _past())
    assert is_expired(vault_path, "OLD_KEY") is True


def test_is_expired_no_expiry(vault_path: str) -> None:
    assert is_expired(vault_path, "NO_EXPIRY") is False


def test_expired_keys_returns_only_past(vault_path: str) -> None:
    set_expiry(vault_path, "STALE", _past(7200))
    set_expiry(vault_path, "FRESH", _future(7200))
    result = expired_keys(vault_path)
    assert "STALE" in result
    assert "FRESH" not in result


def test_expired_keys_empty_when_none_expired(vault_path: str) -> None:
    set_expiry(vault_path, "A", _future())
    set_expiry(vault_path, "B", _future(100))
    assert expired_keys(vault_path) == []


def test_list_expiries_returns_all(vault_path: str) -> None:
    set_expiry(vault_path, "X", _future(100))
    set_expiry(vault_path, "Y", _past(100))
    mapping = list_expiries(vault_path)
    assert set(mapping.keys()) == {"X", "Y"}
    assert all(isinstance(v, datetime) for v in mapping.values())


def test_list_expiries_empty_when_no_file(vault_path: str) -> None:
    assert list_expiries(vault_path) == {}


def test_expiry_stored_as_utc(vault_path: str) -> None:
    naive_dt = datetime(2030, 6, 1, 12, 0, 0)  # naive, no tzinfo
    local_aware = naive_dt.replace(tzinfo=timezone.utc)
    set_expiry(vault_path, "TZ_KEY", local_aware)
    result = get_expiry(vault_path, "TZ_KEY")
    assert result.tzinfo is not None
