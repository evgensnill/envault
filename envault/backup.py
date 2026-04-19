"""Backup and restore vault files to/from an archive."""
from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

META_FILE = "backup_meta.json"


def _meta(vault_path: Path, label: str | None) -> dict:
    return {
        "vault": str(vault_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label or "",
    }


def create_backup(vault_path: Path, dest_dir: Path, label: str | None = None) -> Path:
    """Archive the vault file into dest_dir and return the archive path."""
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = f"_{label}" if label else ""
    archive_path = dest_dir / f"backup_{ts}{slug}.tar.gz"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        meta_file = tmp_path / META_FILE
        meta_file.write_text(json.dumps(_meta(vault_path, label), indent=2))
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(vault_path, arcname=vault_path.name)
            tar.add(meta_file, arcname=META_FILE)
    return archive_path


def list_backups(dest_dir: Path) -> list[dict]:
    """Return metadata for all backups in dest_dir, newest first."""
    dest_dir = Path(dest_dir)
    if not dest_dir.exists():
        return []
    results = []
    for archive in sorted(dest_dir.glob("backup_*.tar.gz"), reverse=True):
        try:
            with tarfile.open(archive, "r:gz") as tar:
                member = tar.getmember(META_FILE)
                f = tar.extractfile(member)
                meta = json.loads(f.read()) if f else {}
        except Exception:
            meta = {}
        meta["archive"] = str(archive)
        results.append(meta)
    return results


def restore_backup(archive_path: Path, target_dir: Path, overwrite: bool = False) -> Path:
    """Extract vault file from archive into target_dir."""
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as tar:
        members = [m for m in tar.getmembers() if m.name != META_FILE]
        if not members:
            raise ValueError("Archive contains no vault file.")
        vault_member = members[0]
        dest = target_dir / vault_member.name
        if dest.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {dest}. Use overwrite=True.")
        tar.extract(vault_member, path=target_dir)
    return dest
