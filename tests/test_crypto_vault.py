"""Tests for crypto and vault modules."""

import json
import pytest
from pathlib import Path

from envault.crypto import encrypt, decrypt
from envault.vault import Vault


PASSWORD = "correct-horse-battery-staple"
WRONG_PASSWORD = "wrong-password"


# --- crypto tests ---

def test_encrypt_decrypt_roundtrip():
    plaintext = "super_secret_value"
    token = encrypt(plaintext, PASSWORD)
    assert decrypt(token, PASSWORD) == plaintext


def test_encrypt_produces_different_tokens():
    """Each call should produce a unique token due to random salt/nonce."""
    t1 = encrypt("value", PASSWORD)
    t2 = encrypt("value", PASSWORD)
    assert t1 != t2


def test_decrypt_wrong_password_raises():
    token = encrypt("secret", PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, WRONG_PASSWORD)


def test_decrypt_invalid_token_raises():
    with pytest.raises(ValueError):
        decrypt("not-a-valid-token!!", PASSWORD)


def test_decrypt_short_token_raises():
    import base64
    short = base64.urlsafe_b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="too short"):
        decrypt(short, PASSWORD)


# --- vault tests ---

def test_vault_set_get(tmp_path):
    vault = Vault(path=tmp_path / "vault.json")
    vault.load(PASSWORD)  # empty vault
    vault.set("DB_PASSWORD", "s3cr3t")
    assert vault.get("DB_PASSWORD") == "s3cr3t"


def test_vault_persist_and_reload(tmp_path):
    path = tmp_path / "vault.json"
    vault = Vault(path=path)
    vault.load(PASSWORD)
    vault.set("API_KEY", "abc123")
    vault.save(PASSWORD)

    vault2 = Vault(path=path)
    vault2.load(PASSWORD)
    assert vault2.get("API_KEY") == "abc123"


def test_vault_delete(tmp_path):
    vault = Vault(path=tmp_path / "vault.json")
    vault.load(PASSWORD)
    vault.set("KEY", "value")
    vault.delete("KEY")
    assert "KEY" not in vault.list_keys()


def test_vault_delete_missing_key_raises(tmp_path):
    vault = Vault(path=tmp_path / "vault.json")
    vault.load(PASSWORD)
    with pytest.raises(KeyError):
        vault.delete("NONEXISTENT")


def test_vault_wrong_password_on_load(tmp_path):
    path = tmp_path / "vault.json"
    vault = Vault(path=path)
    vault.load(PASSWORD)
    vault.set("SECRET", "value")
    vault.save(PASSWORD)

    vault2 = Vault(path=path)
    with pytest.raises(ValueError):
        vault2.load(WRONG_PASSWORD)
