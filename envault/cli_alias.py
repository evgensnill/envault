"""CLI commands for managing key aliases in the vault."""

import click
from envault.cli import _get_vault, cli
from envault.alias import add_alias, remove_alias, resolve_alias, list_aliases


@cli.group("alias")
def alias():
    """Manage key aliases."""


@alias.command("add")
@click.argument("alias_name")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def add_cmd(alias_name, key, vault_path, password):
    """Add an alias NAME pointing to KEY."""
    vault = _get_vault(vault_path, password)
    try:
        add_alias(vault, alias_name, key)
        click.echo(f"Alias '{alias_name}' -> '{key}' added.")
    except KeyError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))


@alias.command("remove")
@click.argument("alias_name")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault file.")
def remove_cmd(alias_name, vault_path):
    """Remove alias NAME."""
    vault = _get_vault.__wrapped__(vault_path, password=None) if hasattr(_get_vault, "__wrapped__") else None
    # alias store is keyed by vault path; no decryption needed
    removed = remove_alias(vault_path, alias_name)
    if removed:
        click.echo(f"Alias '{alias_name}' removed.")
    else:
        click.echo(f"Alias '{alias_name}' not found.", err=True)


@alias.command("resolve")
@click.argument("alias_name")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def resolve_cmd(alias_name, vault_path, password):
    """Resolve alias NAME to its value."""
    vault = _get_vault(vault_path, password)
    try:
        value = resolve_alias(vault, alias_name)
        click.echo(value)
    except KeyError as exc:
        raise click.ClickException(str(exc))


@alias.command("list")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault file.")
def list_cmd(vault_path):
    """List all aliases defined for the vault."""
    aliases = list_aliases(vault_path)
    if not aliases:
        click.echo("No aliases defined.")
        return
    max_len = max(len(a) for a in aliases)
    for alias_name, key in sorted(aliases.items()):
        click.echo(f"  {alias_name:<{max_len}}  ->  {key}")
