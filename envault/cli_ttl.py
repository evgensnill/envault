"""CLI commands for managing secret TTLs."""
from __future__ import annotations

import time

import click

from envault.cli import _get_vault
from envault import ttl as ttl_mod


@click.group("ttl")
def ttl():
    """Manage time-to-live for secrets."""


@ttl.command("set")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--vault", default="vault.db", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def set_cmd(key: str, seconds: int, vault: str, password: str):
    """Set a TTL of SECONDS on KEY."""
    v = _get_vault(vault, password)
    if key not in v.list_keys():
        raise click.ClickException(f"Key '{key}' not found in vault.")
    ttl_mod.set_ttl(vault, key, seconds)
    click.echo(f"TTL of {seconds}s set for '{key}'.")


@ttl.command("get")
@click.argument("key")
@click.option("--vault", default="vault.db", show_default=True)
def get_cmd(key: str, vault: str):
    """Show TTL information for KEY."""
    meta = ttl_mod.get_ttl(vault, key)
    if meta is None:
        click.echo(f"No TTL set for '{key}'.")
        return
    remaining = max(0.0, meta["expires_at"] - time.time())
    status = "EXPIRED" if remaining == 0 else f"{remaining:.0f}s remaining"
    click.echo(f"Key: {key}  TTL: {meta['ttl_seconds']}s  Status: {status}")


@ttl.command("remove")
@click.argument("key")
@click.option("--vault", default="vault.db", show_default=True)
def remove_cmd(key: str, vault: str):
    """Remove the TTL for KEY."""
    removed = ttl_mod.remove_ttl(vault, key)
    if removed:
        click.echo(f"TTL removed for '{key}'.")
    else:
        click.echo(f"No TTL was set for '{key}'.")


@ttl.command("list")
@click.option("--vault", default="vault.db", show_default=True)
def list_cmd(vault: str):
    """List all keys that have a TTL configured."""
    records = ttl_mod.list_ttls(vault)
    if not records:
        click.echo("No TTLs configured.")
        return
    now = time.time()
    for key, meta in records.items():
        remaining = max(0.0, meta["expires_at"] - now)
        status = "EXPIRED" if remaining == 0 else f"{remaining:.0f}s"
        click.echo(f"{key:30s}  ttl={meta['ttl_seconds']}s  remaining={status}")


@ttl.command("expired")
@click.option("--vault", default="vault.db", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def expired_cmd(vault: str, password: str):
    """List all keys whose TTL has elapsed."""
    v = _get_vault(vault, password)
    expired = ttl_mod.expired_keys(vault, v.list_keys())
    if not expired:
        click.echo("No expired keys.")
    else:
        for k in expired:
            click.echo(k)
