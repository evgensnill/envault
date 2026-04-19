"""Tests for envault.profile module."""
import pytest
from unittest.mock import patch
from envault import profile as prof


@pytest.fixture(autouse=True)
def isolated_profiles(tmp_path, monkeypatch):
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setattr(prof, "_PROFILES_FILE", profiles_file)
    yield profiles_file


def test_add_and_get_profile():
    prof.add_profile("dev", "/tmp/dev.vault")
    p = prof.get_profile("dev")
    assert p["vault_path"] == "/tmp/dev.vault"
    assert p["description"] == ""


def test_add_profile_with_description():
    prof.add_profile("prod", "/tmp/prod.vault", description="Production vault")
    p = prof.get_profile("prod")
    assert p["description"] == "Production vault"


def test_get_missing_profile_raises():
    with pytest.raises(KeyError, match="not found"):
        prof.get_profile("nonexistent")


def test_remove_profile():
    prof.add_profile("staging", "/tmp/staging.vault")
    prof.remove_profile("staging")
    with pytest.raises(KeyError):
        prof.get_profile("staging")


def test_remove_missing_profile_raises():
    with pytest.raises(KeyError, match="not found"):
        prof.remove_profile("ghost")


def test_list_profiles_empty():
    assert prof.list_profiles() == []


def test_list_profiles_returns_all():
    prof.add_profile("a", "/a")
    prof.add_profile("b", "/b")
    names = [p["name"] for p in prof.list_profiles()]
    assert "a" in names
    assert "b" in names


def test_set_and_get_default_profile():
    prof.add_profile("dev", "/tmp/dev.vault")
    prof.set_default_profile("dev")
    assert prof.get_default_profile() == "dev"


def test_set_default_missing_profile_raises():
    with pytest.raises(KeyError, match="not found"):
        prof.set_default_profile("missing")


def test_get_default_profile_none_when_unset():
    assert prof.get_default_profile() is None


def test_overwrite_profile():
    prof.add_profile("dev", "/old")
    prof.add_profile("dev", "/new")
    assert prof.get_profile("dev")["vault_path"] == "/new"
