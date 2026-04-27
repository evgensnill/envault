"""CLI commands for vault quota management."""
import click

from envault.cli import _get_vault
from envault.quota import (
    QuotaExceededError,
    check_quota,
    get_quota,
    remove_quota,
    set_quota,
)


@click.group("quota")
def quota():
    """Manage vault key quotas."""


@quota.command("set")
@click.argument("vault_path")
@click.argument("limit", type=int)
def set_cmd(vault_path: str, limit: int):
    """Set the maximum number of keys allowed in VAULT_PATH."""
    try:
        set_quota(vault_path, limit)
        click.echo(f"Quota set to {limit} keys for '{vault_path}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@quota.command("get")
@click.argument("vault_path")
def get_cmd(vault_path: str):
    """Show the current quota limit for VAULT_PATH."""
    limit = get_quota(vault_path)
    if limit is None:
        click.echo("No quota configured.")
    else:
        click.echo(f"Quota limit: {limit} keys")


@quota.command("remove")
@click.argument("vault_path")
def remove_cmd(vault_path: str):
    """Remove the quota limit from VAULT_PATH."""
    removed = remove_quota(vault_path)
    if removed:
        click.echo("Quota removed.")
    else:
        click.echo("No quota was configured.")


@quota.command("check")
@click.argument("vault_path")
@click.option("--password", prompt=True, hide_input=True)
def check_cmd(vault_path: str, password: str):
    """Check current key usage against the quota for VAULT_PATH."""
    vault = _get_vault(vault_path, password)
    try:
        info = check_quota(vault_path, vault)
        click.echo(f"Keys: {info.current}/{info.limit} (remaining: {info.remaining})")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except QuotaExceededError as exc:
        click.echo(f"Warning: {exc}", err=True)
        raise SystemExit(2)
