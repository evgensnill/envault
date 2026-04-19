"""CLI commands for vault backup/restore."""
from __future__ import annotations

from pathlib import Path

import click

from envault.backup import create_backup, list_backups, restore_backup
from envault.cli import _get_vault


@click.group()
def backup():
    """Backup and restore vault files."""


@backup.command("create")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--dest", "dest_dir", required=True, help="Directory to store backup.")
@click.option("--label", default=None, help="Optional label for the backup.")
def create_cmd(vault_path: str, dest_dir: str, label: str | None):
    """Create a backup archive of the vault."""
    try:
        archive = create_backup(Path(vault_path), Path(dest_dir), label)
        click.echo(f"Backup created: {archive}")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@backup.command("list")
@click.option("--dest", "dest_dir", required=True, help="Directory containing backups.")
def list_cmd(dest_dir: str):
    """List available backups."""
    entries = list_backups(Path(dest_dir))
    if not entries:
        click.echo("No backups found.")
        return
    for e in entries:
        label = f" [{e['label']}]" if e.get("label") else ""
        click.echo(f"{e.get('created_at', 'unknown')}{label}  →  {e['archive']}")


@backup.command("restore")
@click.argument("archive")
@click.option("--dest", "dest_dir", required=True, help="Directory to restore vault into.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing vault.")
def restore_cmd(archive: str, dest_dir: str, overwrite: bool):
    """Restore a vault from a backup archive."""
    try:
        path = restore_backup(Path(archive), Path(dest_dir), overwrite)
        click.echo(f"Vault restored to: {path}")
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
