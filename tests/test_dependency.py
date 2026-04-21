"""Tests for envault.dependency."""
import json
import pytest
from pathlib import Path
from envault.vault import Vault
from envault import dependency


def _make_vault(tmp_path: Path, keys: dict, password: str = "pw") -> tuple:
    vault_file = str(tmp_path / "vault.env")
    v = Vault(vault_file, password)
    for k, val in keys.items():
        v.set(k, val)
    v.save()
    return vault_file, v


def test_add_dependency_and_get(tmp_path):
    vp, v = _make_vault(tmp_path, {"DB_URL": "x", "DB_PASS": "y"})
    dependency.add_dependency(vp, "DB_URL", "DB_PASS", v)
    assert "DB_PASS" in dependency.get_dependencies(vp, "DB_URL")


def test_add_dependency_missing_key_raises(tmp_path):
    vp, v = _make_vault(tmp_path, {"DB_URL": "x"})
    with pytest.raises(KeyError):
        dependency.add_dependency(vp, "DB_URL", "MISSING", v)


def test_add_dependency_missing_dependent_raises(tmp_path):
    vp, v = _make_vault(tmp_path, {"DB_PASS": "y"})
    with pytest.raises(KeyError):
        dependency.add_dependency(vp, "MISSING", "DB_PASS", v)


def test_add_dependency_self_raises(tmp_path):
    vp, v = _make_vault(tmp_path, {"DB_URL": "x"})
    with pytest.raises(ValueError):
        dependency.add_dependency(vp, "DB_URL", "DB_URL", v)


def test_add_dependency_idempotent(tmp_path):
    vp, v = _make_vault(tmp_path, {"A": "1", "B": "2"})
    dependency.add_dependency(vp, "A", "B", v)
    dependency.add_dependency(vp, "A", "B", v)
    assert dependency.get_dependencies(vp, "A").count("B") == 1


def test_remove_dependency_returns_true(tmp_path):
    vp, v = _make_vault(tmp_path, {"A": "1", "B": "2"})
    dependency.add_dependency(vp, "A", "B", v)
    result = dependency.remove_dependency(vp, "A", "B")
    assert result is True
    assert dependency.get_dependencies(vp, "A") == []


def test_remove_nonexistent_dependency_returns_false(tmp_path):
    vp, v = _make_vault(tmp_path, {"A": "1", "B": "2"})
    result = dependency.remove_dependency(vp, "A", "B")
    assert result is False


def test_get_dependents(tmp_path):
    vp, v = _make_vault(tmp_path, {"A": "1", "B": "2", "C": "3"})
    dependency.add_dependency(vp, "A", "B", v)
    dependency.add_dependency(vp, "C", "B", v)
    dependents = dependency.get_dependents(vp, "B")
    assert set(dependents) == {"A", "C"}


def test_get_dependencies_no_file_returns_empty(tmp_path):
    vp = str(tmp_path / "vault.env")
    assert dependency.get_dependencies(vp, "X") == []


def test_all_dependencies(tmp_path):
    vp, v = _make_vault(tmp_path, {"A": "1", "B": "2", "C": "3"})
    dependency.add_dependency(vp, "A", "B", v)
    dependency.add_dependency(vp, "A", "C", v)
    all_deps = dependency.all_dependencies(vp)
    assert all_deps == {"A": ["B", "C"]}
