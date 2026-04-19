"""Tests for envault.env_check."""
from __future__ import annotations

import os
import pytest

from envault.env_check import check_env, EnvCheckResult


class _FakeVault:
    def __init__(self, store: dict):
        self._store = store

    def list_keys(self):
        return list(self._store.keys())

    def get(self, key):
        return self._store[key]


def _make_vault(**kw):
    return _FakeVault(kw)


def test_all_ok(monkeypatch):
    vault = _make_vault(FOO="bar", BAZ="qux")
    monkeypatch.setenv("FOO", "bar")
    monkeypatch.setenv("BAZ", "qux")
    results = check_env(vault)
    assert all(r.status == "ok" for r in results)


def test_missing_key(monkeypatch):
    vault = _make_vault(SECRET="abc")
    monkeypatch.delenv("SECRET", raising=False)
    results = check_env(vault)
    assert results[0].status == "missing"
    assert results[0].vault_value == "abc"
    assert results[0].env_value is None


def test_mismatch(monkeypatch):
    vault = _make_vault(TOKEN="correct")
    monkeypatch.setenv("TOKEN", "wrong")
    results = check_env(vault)
    assert results[0].status == "mismatch"
    assert results[0].vault_value == "correct"
    assert results[0].env_value == "wrong"


def test_subset_of_keys(monkeypatch):
    vault = _make_vault(A="1", B="2", C="3")
    monkeypatch.setenv("A", "1")
    monkeypatch.delenv("B", raising=False)
    results = check_env(vault, keys=["A", "B"])
    assert len(results) == 2
    statuses = {r.key: r.status for r in results}
    assert statuses["A"] == "ok"
    assert statuses["B"] == "missing"


def test_empty_vault():
    vault = _make_vault()
    results = check_env(vault)
    assert results == []
