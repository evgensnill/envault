"""CLI commands for vault lock management."""

from __future__ import annotations

from pathlib import Path

import click

from envault.lock import acquire_lock, is_locked, lock_info, release_lock


@click.group("lock")
def lock() -> None:
    """Manage vault file locks."""


@lock.command("acquire")
@click.argument("vault_path", type=click.Path())
@click.option("--timeout", default=10.0, show_default=True, help="Seconds to wait.")
def acquire_cmd(vault_path: str, timeout: float) -> None:
    """Acquire the lock for VAULT_PATH."""
    path = Path(vault_path)
    try:
        acquire_lock(path, timeout=timeout)
        click.echo(f"Lock acquired for '{path}'.")
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc


@lock.command("release")
@click.argument("vault_path", type=click.Path())
def release_cmd(vault_path: str) -> None:
    """Release the lock for VAULT_PATH."""
    path = Path(vault_path)
    release_lock(path)
    click.echo(f"Lock released for '{path}'.")


@lock.command("status")
@click.argument("vault_path", type=click.Path())
def status_cmd(vault_path: str) -> None:
    """Show lock status for VAULT_PATH."""
    path = Path(vault_path)
    if not is_locked(path):
        click.echo(f"'{path}' is NOT locked.")
        return

    info = lock_info(path)
    if info:
        import datetime

        ts = datetime.datetime.fromtimestamp(info["acquired_at"]).isoformat()
        click.echo(f"'{path}' is LOCKED — pid={info['pid']}, acquired={ts}")
    else:
        click.echo(f"'{path}' is LOCKED (no metadata available).")


@lock.command("force-release")
@click.argument("vault_path", type=click.Path())
def force_release_cmd(vault_path: str) -> None:
    """Forcibly remove the lock file for VAULT_PATH (use with caution)."""
    path = Path(vault_path)
    release_lock(path)
    click.echo(f"Lock forcibly released for '{path}'.")
