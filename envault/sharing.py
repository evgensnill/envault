"""Vault sharing: export an encrypted bundle and import it on another machine."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Dict

from envault.crypto import derive_key, encrypt, decrypt
from envault.vault import Vault


def export_bundle(vault: Vault, share_password: str) -> str:
    """Serialize all plaintext secrets into a base64-encoded encrypted bundle."""
    plaintext_store: Dict[str, str] = {}
    for key in vault.keys():
        plaintext_store[key] = vault.get(key)

    payload = json.dumps(plaintext_store).encode()
    salt = os.urandom(16)
    key = derive_key(share_password, salt)
    token = encrypt(key, payload)

    bundle = {
        "salt": base64.b64encode(salt).decode(),
        "token": base64.b64encode(token).decode(),
    }
    return base64.b64encode(json.dumps(bundle).encode()).decode()


def import_bundle(
    vault: Vault,
    bundle_b64: str,
    share_password: str,
    overwrite: bool = False,
) -> list[str]:
    """Decrypt a bundle and load secrets into *vault*.

    Returns the list of keys that were imported.
    """
    try:
        bundle = json.loads(base64.b64decode(bundle_b64))
        salt = base64.b64decode(bundle["salt"])
        token = base64.b64decode(bundle["token"])
    except Exception as exc:
        raise ValueError(f"Malformed bundle: {exc}") from exc

    key = derive_key(share_password, salt)
    raw = decrypt(key, token)  # raises InvalidToken on bad password
    store: Dict[str, str] = json.loads(raw)

    imported: list[str] = []
    for k, v in store.items():
        if not overwrite and k in vault.keys():
            continue
        vault.set(k, v)
        imported.append(k)

    vault.save()
    return imported
