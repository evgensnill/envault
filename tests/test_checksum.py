"""Tests for envault.checksum."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.checksum import (
    get_checksum,
    list_checksums,
    record_checksum,
    remove_checksum,
    verify_checksum,
    _checksum_path,
    _hash,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> str:
    return str(tmp_path / "test.vault")


def test_record_creates_checksum_file(vault_path: str) -> None:
    record_checksum(vault_path, "API_KEY", "supersecret")
    assert _checksum_path(vault_path).exists()


def test_record_returns_hex_digest(vault_path: str) -> None:
    digest = record_checksum(vault_path, "API_KEY", "value123")
    assert digest == _hash("value123")
    assert len(digest) == 64  # sha256 hex


def test_get_checksum_returns_stored_value(vault_path: str) -> None:
    record_checksum(vault_path, "DB_PASS", "hunter2")
    stored = get_checksum(vault_path, "DB_PASS")
    assert stored == _hash("hunter2")


def test_get_checksum_missing_key_returns_none(vault_path: str) -> None:
    assert get_checksum(vault_path, "NONEXISTENT") is None


def test_verify_checksum_correct_value(vault_path: str) -> None:
    record_checksum(vault_path, "TOKEN", "abc123")
    assert verify_checksum(vault_path, "TOKEN", "abc123") is True


def test_verify_checksum_wrong_value(vault_path: str) -> None:
    record_checksum(vault_path, "TOKEN", "abc123")
    assert verify_checksum(vault_path, "TOKEN", "wrong") is False


def test_verify_checksum_no_record_returns_false(vault_path: str) -> None:
    assert verify_checksum(vault_path, "MISSING", "anything") is False


def test_remove_checksum_returns_true_when_present(vault_path: str) -> None:
    record_checksum(vault_path, "KEY", "val")
    assert remove_checksum(vault_path, "KEY") is True
    assert get_checksum(vault_path, "KEY") is None


def test_remove_checksum_returns_false_when_absent(vault_path: str) -> None:
    assert remove_checksum(vault_path, "GHOST") is False


def test_list_checksums_empty_when_no_file(vault_path: str) -> None:
    assert list_checksums(vault_path) == {}


def test_list_checksums_returns_all_entries(vault_path: str) -> None:
    record_checksum(vault_path, "A", "val_a")
    record_checksum(vault_path, "B", "val_b")
    result = list_checksums(vault_path)
    assert set(result.keys()) == {"A", "B"}
    assert result["A"] == _hash("val_a")
    assert result["B"] == _hash("val_b")


def test_overwrite_updates_checksum(vault_path: str) -> None:
    record_checksum(vault_path, "KEY", "old_value")
    record_checksum(vault_path, "KEY", "new_value")
    assert verify_checksum(vault_path, "KEY", "new_value") is True
    assert verify_checksum(vault_path, "KEY", "old_value") is False
