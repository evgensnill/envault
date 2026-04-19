"""Tests for envault.tags module."""
import pytest
from pathlib import Path
from envault.vault import Vault
from envault.tags import add_tag, remove_tag, get_tags, keys_by_tag, all_tags

PASSWORD = "test-pass"


def _make_vault(tmp_path: Path) -> Vault:
    v = Vault(tmp_path / "vault.db", PASSWORD)
    v.set("API_KEY", "abc123")
    v.set("DB_URL", "postgres://localhost/db")
    v.set("SECRET", "topsecret")
    return v


def test_add_tag_and_get_tags(tmp_path):
    v = _make_vault(tmp_path)
    add_tag(v, "API_KEY", "production")
    assert "production" in get_tags(v, "API_KEY")


def test_add_duplicate_tag_is_idempotent(tmp_path):
    v = _make_vault(tmp_path)
    add_tag(v, "API_KEY", "production")
    add_tag(v, "API_KEY", "production")
    assert get_tags(v, "API_KEY").count("production") == 1


def test_add_tag_missing_key_raises(tmp_path):
    v = _make_vault(tmp_path)
    with pytest.raises(KeyError):
        add_tag(v, "NONEXISTENT", "mytag")


def test_remove_tag(tmp_path):
    v = _make_vault(tmp_path)
    add_tag(v, "DB_URL", "database")
    remove_tag(v, "DB_URL", "database")
    assert "database" not in get_tags(v, "DB_URL")


def test_remove_nonexistent_tag_is_safe(tmp_path):
    v = _make_vault(tmp_path)
    remove_tag(v, "API_KEY", "ghost")  # should not raise
    assert get_tags(v, "API_KEY") == []


def test_keys_by_tag(tmp_path):
    v = _make_vault(tmp_path)
    add_tag(v, "API_KEY", "sensitive")
    add_tag(v, "SECRET", "sensitive")
    add_tag(v, "DB_URL", "infra")
    result = keys_by_tag(v, "sensitive")
    assert set(result) == {"API_KEY", "SECRET"}


def test_keys_by_tag_no_match(tmp_path):
    v = _make_vault(tmp_path)
    assert keys_by_tag(v, "nonexistent") == []


def test_all_tags(tmp_path):
    v = _make_vault(tmp_path)
    add_tag(v, "API_KEY", "production")
    add_tag(v, "DB_URL", "infra")
    tags = all_tags(v)
    assert tags["API_KEY"] == ["production"]
    assert tags["DB_URL"] == ["infra"]


def test_get_tags_empty(tmp_path):
    v = _make_vault(tmp_path)
    assert get_tags(v, "API_KEY") == []
