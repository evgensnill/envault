"""Tests for envault.sharing."""
from __future__ import annotations

import json
import pytest

from envault.vault import Vault
from envault.sharing import export_bundle, import_bundle
from cryptography.fernet import InvalidToken


def _make_vault(tmp_path, password="pass", data=None):
    path = tmp_path / "vault"
    v = Vault(str(path), password)
    v.save()
    if data:
        for k, val in data.items():
            v.set(k, val)
        v.save()
    return v


def test_export_returns_string(tmp_path):
    vault = _make_vault(tmp_path, data={"KEY": "value"})
    bundle = export_bundle(vault, "sharepass")
    assert isinstance(bundle, str)
    assert len(bundle) > 0


def test_export_import_roundtrip(tmp_path):
    src = _make_vault(tmp_path / "src", data={"A": "1", "B": "2"})
    bundle = export_bundle(src, "sharepass")

    dst = _make_vault(tmp_path / "dst")
    imported = import_bundle(dst, bundle, "sharepass")

    assert sorted(imported) == ["A", "B"]
    assert dst.get("A") == "1"
    assert dst.get("B") == "2"


def test_import_wrong_share_password_raises(tmp_path):
    src = _make_vault(tmp_path / "src", data={"X": "secret"})
    bundle = export_bundle(src, "correct")

    dst = _make_vault(tmp_path / "dst")
    with pytest.raises(InvalidToken):
        import_bundle(dst, bundle, "wrong")


def test_import_no_overwrite_skips_existing(tmp_path):
    src = _make_vault(tmp_path / "src", data={"KEY": "new_value"})
    bundle = export_bundle(src, "pw")

    dst = _make_vault(tmp_path / "dst", data={"KEY": "old_value"})
    imported = import_bundle(dst, bundle, "pw", overwrite=False)

    assert imported == []
    assert dst.get("KEY") == "old_value"


def test_import_overwrite_replaces_existing(tmp_path):
    src = _make_vault(tmp_path / "src", data={"KEY": "new_value"})
    bundle = export_bundle(src, "pw")

    dst = _make_vault(tmp_path / "dst", data={"KEY": "old_value"})
    imported = import_bundle(dst, bundle, "pw", overwrite=True)

    assert "KEY" in imported
    assert dst.get("KEY") == "new_value"


def test_malformed_bundle_raises(tmp_path):
    dst = _make_vault(tmp_path)
    with pytest.raises(ValueError, match="Malformed bundle"):
        import_bundle(dst, "not-a-valid-bundle!!", "pw")


def test_export_empty_vault(tmp_path):
    vault = _make_vault(tmp_path)
    bundle = export_bundle(vault, "pw")
    dst = _make_vault(tmp_path / "dst")
    imported = import_bundle(dst, bundle, "pw")
    assert imported == []
