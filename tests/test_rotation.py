"""Tests for envault.rotation module."""
from __future__ import annotations

import datetime
import pytest
from unittest.mock import MagicMock, patch

from envault.rotation import (
    record_rotation,
    last_rotated,
    rotate_key,
    keys_older_than,
    get_rotation_meta,
)


def _make_vault():
    """Return a simple in-memory vault mock."""
    store: dict = {}

    vault = MagicMock()
    vault.get.side_effect = lambda k: store[k]
    vault.set.side_effect = lambda k, v: store.update({k: v})
    return vault


def test_record_and_last_rotated():
    vault = _make_vault()
    before = datetime.datetime.utcnow()
    record_rotation(vault, "DB_PASSWORD")
    after = datetime.datetime.utcnow()
    ts = last_rotated(vault, "DB_PASSWORD")
    assert ts is not None
    assert before <= ts <= after


def test_last_rotated_missing_key():
    vault = _make_vault()
    assert last_rotated(vault, "NONEXISTENT") is None


def test_rotate_key_updates_value():
    vault = _make_vault()
    rotate_key(vault, "API_KEY", "new-secret-value")
    vault.set.assert_any_call("API_KEY", "new-secret-value")


def test_rotate_key_records_timestamp():
    vault = _make_vault()
    rotate_key(vault, "API_KEY", "new-secret-value")
    ts = last_rotated(vault, "API_KEY")
    assert ts is not None


def test_keys_older_than_returns_stale():
    vault = _make_vault()
    old_ts = (datetime.datetime.utcnow() - datetime.timedelta(days=100)).isoformat()
    import json
    from envault.rotation import ROTATION_META_KEY
    vault.get.side_effect = lambda k: json.dumps({"OLD_KEY": old_ts}) if k == ROTATION_META_KEY else (_ for _ in ()).throw(KeyError(k))
    stale = keys_older_than(vault, 90)
    assert "OLD_KEY" in stale


def test_keys_older_than_ignores_fresh():
    vault = _make_vault()
    rotate_key(vault, "FRESH_KEY", "value")
    stale = keys_older_than(vault, 90)
    assert "FRESH_KEY" not in stale


def test_get_rotation_meta_empty_on_missing():
    vault = _make_vault()
    meta = get_rotation_meta(vault)
    assert meta == {}
