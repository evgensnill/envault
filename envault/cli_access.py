"""CLI commands for access control."""
import click
from envault.cli import _get_vault
from envault.access import add_rule, remove_rule, load_rules


@click.group()
def access():
    """Manage key-level access rules."""


@access.command("add")
@click.argument("key")
@click.argument("permission", type=click.Choice(["read", "write", "deny"]))
@click.option("--identity", default="default", show_default=True)
@click.option("--vault", default="vault.db", show_default=True)
@click.password_option(prompt="Vault password")
def add_cmd(key, permission, identity, vault, password):
    """Add or update an access rule for KEY."""
    v = _get_vault(vault, password)
    if key not in v.list_keys():
        raise click.ClickException(f"Key '{key}' not found in vault.")
    add_rule(vault, key, permission, identity)
    click.echo(f"Rule set: {identity} -> {key} = {permission}")


@access.command("remove")
@click.argument("key")
@click.option("--identity", default="default", show_default=True)
@click.option("--vault", default="vault.db", show_default=True)
def remove_cmd(key, identity, vault):
    """Remove an access rule for KEY."""
    remove_rule(vault, key, identity)
    click.echo(f"Rule removed: {identity} -> {key}")


@access.command("list")
@click.option("--vault", default="vault.db", show_default=True)
def list_cmd(vault):
    """List all access rules."""
    rules = load_rules(vault)
    if not rules:
        click.echo("No access rules defined.")
        return
    for r in rules:
        click.echo(f"{r.identity:20s}  {r.key:30s}  {r.permission}")
