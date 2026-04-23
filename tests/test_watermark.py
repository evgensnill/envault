"""Tests for envault.watermark."""
import pytest
from pathlib import Path

from envault.watermark import (
    set_watermark,
    get_watermark,
    verify_watermark,
    remove_watermark,
    _wm_path,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> str:
    p = tmp_path / "test.vault"
    p.write_text("{}")
    return str(p)


def test_set_watermark_returns_token(vault_path: str) -> None:
    token = set_watermark(vault_path, "alice")
    assert isinstance(token, str)
    assert len(token) == 16


def test_set_watermark_creates_file(vault_path: str) -> None:
    set_watermark(vault_path, "alice")
    assert _wm_path(vault_path).exists()


def test_get_watermark_returns_none_when_absent(vault_path: str) -> None:
    assert get_watermark(vault_path) is None


def test_get_watermark_returns_record(vault_path: str) -> None:
    set_watermark(vault_path, "bob")
    record = get_watermark(vault_path)
    assert record is not None
    assert record["identity"] == "bob"
    assert len(record["token"]) == 16


def test_verify_watermark_correct_identity(vault_path: str) -> None:
    set_watermark(vault_path, "carol")
    assert verify_watermark(vault_path, "carol") is True


def test_verify_watermark_wrong_identity(vault_path: str) -> None:
    set_watermark(vault_path, "carol")
    assert verify_watermark(vault_path, "eve") is False


def test_verify_watermark_no_watermark(vault_path: str) -> None:
    assert verify_watermark(vault_path, "anyone") is False


def test_token_is_deterministic(vault_path: str) -> None:
    t1 = set_watermark(vault_path, "dave")
    t2 = set_watermark(vault_path, "dave")
    assert t1 == t2


def test_different_identities_produce_different_tokens(vault_path: str) -> None:
    t1 = set_watermark(vault_path, "alice")
    t2 = set_watermark(vault_path, "bob")
    assert t1 != t2


def test_remove_watermark_returns_true(vault_path: str) -> None:
    set_watermark(vault_path, "alice")
    assert remove_watermark(vault_path) is True
    assert not _wm_path(vault_path).exists()


def test_remove_watermark_returns_false_when_absent(vault_path: str) -> None:
    assert remove_watermark(vault_path) is False


def test_get_watermark_after_remove_returns_none(vault_path: str) -> None:
    set_watermark(vault_path, "alice")
    remove_watermark(vault_path)
    assert get_watermark(vault_path) is None
