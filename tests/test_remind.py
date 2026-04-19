"""Tests for envault.remind."""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from envault.remind import check_reminders, overdue_keys, ReminderEntry


class _FakeVault:
    def __init__(self, keys):
        self._keys = keys

    def list_keys(self):
        return list(self._keys)


NOW = datetime(2024, 6, 1, 12, 0, 0)


def _patch_last_rotated(mapping):
    """mapping: key -> datetime or None"""
    return patch("envault.remind.last_rotated", side_effect=lambda v, k: mapping.get(k))


def test_never_rotated_is_overdue():
    vault = _FakeVault(["API_KEY"])
    with _patch_last_rotated({"API_KEY": None}), patch("envault.remind.datetime") as mock_dt:
        mock_dt.utcnow.return_value = NOW
        entries = check_reminders(vault, max_age_days=90)
    assert len(entries) == 1
    e = entries[0]
    assert e.key == "API_KEY"
    assert e.overdue is True
    assert e.last_rotated is None
    assert e.days_since is None


def test_recently_rotated_not_overdue():
    vault = _FakeVault(["DB_PASS"])
    rotated = NOW - timedelta(days=10)
    with _patch_last_rotated({"DB_PASS": rotated}), patch("envault.remind.datetime") as mock_dt:
        mock_dt.utcnow.return_value = NOW
        entries = check_reminders(vault, max_age_days=90)
    e = entries[0]
    assert e.overdue is False
    assert e.days_since == 10
    assert e.due_in == 80


def test_old_rotation_is_overdue():
    vault = _FakeVault(["TOKEN"])
    rotated = NOW - timedelta(days=100)
    with _patch_last_rotated({"TOKEN": rotated}), patch("envault.remind.datetime") as mock_dt:
        mock_dt.utcnow.return_value = NOW
        entries = check_reminders(vault, max_age_days=90)
    e = entries[0]
    assert e.overdue is True
    assert e.due_in == -10


def test_overdue_keys_returns_only_overdue():
    vault = _FakeVault(["A", "B", "C"])
    mapping = {
        "A": NOW - timedelta(days=5),
        "B": None,
        "C": NOW - timedelta(days=95),
    }
    with _patch_last_rotated(mapping), patch("envault.remind.datetime") as mock_dt:
        mock_dt.utcnow.return_value = NOW
        result = overdue_keys(vault, max_age_days=90)
    assert set(result) == {"B", "C"}
    assert "A" not in result


def test_check_reminders_subset_of_keys():
    vault = _FakeVault(["X", "Y", "Z"])
    mapping = {"X": None, "Y": None, "Z": None}
    with _patch_last_rotated(mapping), patch("envault.remind.datetime") as mock_dt:
        mock_dt.utcnow.return_value = NOW
        entries = check_reminders(vault, keys=["X", "Z"])
    assert [e.key for e in entries] == ["X", "Z"]


def test_check_reminders_empty_vault():
    vault = _FakeVault([])
    with _patch_last_rotated({}), patch("envault.remind.datetime") as mock_dt:
        mock_dt.utcnow.return_value = NOW
        entries = check_reminders(vault)
    assert entries == []
