"""CLI commands for managing redacted (masked) keys in a vault."""

import click
from envault.cli import _get_vault
from envault.redact import (
    mark_redacted,
    unmark_redacted,
    is_redacted,
    list_redacted,
    redact_display,
    get_redact_meta,
)


@click.group("redact")
def redact():
    """Manage redacted (masked) vault keys."""


@redact.command("mark")
@click.argument("vault_path")
@click.argument("key")
@click.option("--reason", "-r", default="", help="Optional reason for redacting this key.")
@click.password_option("--password", "-p", prompt=True, help="Vault password.")
def mark_cmd(vault_path, key, reason, password):
    """Mark a key as redacted so its value is masked in output."""
    vault = _get_vault(vault_path, password)
    try:
        mark_redacted(vault_path, key, reason=reason, vault=vault)
        click.echo(f"Key '{key}' marked as redacted.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@redact.command("unmark")
@click.argument("vault_path")
@click.argument("key")
@click.password_option("--password", "-p", prompt=True, help="Vault password.")
def unmark_cmd(vault_path, key, password):
    """Remove the redacted mark from a key."""
    _get_vault(vault_path, password)  # validate password
    removed = unmark_redacted(vault_path, key)
    if removed:
        click.echo(f"Key '{key}' is no longer redacted.")
    else:
        click.echo(f"Key '{key}' was not redacted.")


@redact.command("status")
@click.argument("vault_path")
@click.argument("key")
@click.password_option("--password", "-p", prompt=True, help="Vault password.")
def status_cmd(vault_path, key, password):
    """Show whether a key is redacted and any associated metadata."""
    _get_vault(vault_path, password)
    if is_redacted(vault_path, key):
        meta = get_redact_meta(vault_path, key)
        click.echo(f"Key '{key}' is REDACTED.")
        if meta.get("reason"):
            click.echo(f"  Reason : {meta['reason']}")
        if meta.get("redacted_at"):
            click.echo(f"  Since  : {meta['redacted_at']}")
    else:
        click.echo(f"Key '{key}' is not redacted.")


@redact.command("list")
@click.argument("vault_path")
@click.password_option("--password", "-p", prompt=True, help="Vault password.")
def list_cmd(vault_path, password):
    """List all redacted keys in the vault."""
    _get_vault(vault_path, password)
    keys = list_redacted(vault_path)
    if not keys:
        click.echo("No redacted keys.")
        return
    click.echo(f"{len(keys)} redacted key(s):")
    for k in keys:
        meta = get_redact_meta(vault_path, k)
        reason = f"  # {meta['reason']}" if meta.get("reason") else ""
        click.echo(f"  {k}{reason}")


@redact.command("show")
@click.argument("vault_path")
@click.argument("key")
@click.option(
    "--reveal", is_flag=True, default=False, help="Show the real value instead of the mask."
)
@click.password_option("--password", "-p", prompt=True, help="Vault password.")
def show_cmd(vault_path, key, reveal, password):
    """Display a key's value, masking it if it is redacted (unless --reveal is set)."""
    vault = _get_vault(vault_path, password)
    try:
        value = vault.get(key)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if reveal or not is_redacted(vault_path, key):
        click.echo(value)
    else:
        click.echo(redact_display(value))
