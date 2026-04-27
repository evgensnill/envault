"""CLI commands for key grouping."""
from __future__ import annotations

import click

from envault.cli import _get_vault
from envault.group import (
    add_to_group,
    delete_group,
    get_group,
    list_groups,
    remove_from_group,
)


@click.group("group")
def group() -> None:
    """Manage key groups."""


@group.command("add")
@click.argument("group_name")
@click.argument("key")
@click.option("--vault", "vault_path", default="vault.db", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def add_cmd(group_name: str, key: str, vault_path: str, password: str) -> None:
    """Add KEY to GROUP_NAME."""
    v = _get_vault(vault_path, password)
    try:
        add_to_group(vault_path, group_name, key, v.list_keys())
        click.echo(f"Added '{key}' to group '{group_name}'.")
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@group.command("remove")
@click.argument("group_name")
@click.argument("key")
@click.option("--vault", "vault_path", default="vault.db", show_default=True)
def remove_cmd(group_name: str, key: str, vault_path: str) -> None:
    """Remove KEY from GROUP_NAME."""
    removed = remove_from_group(vault_path, group_name, key)
    if removed:
        click.echo(f"Removed '{key}' from group '{group_name}'.")
    else:
        click.echo(f"Key '{key}' was not in group '{group_name}'.")


@group.command("list")
@click.option("--vault", "vault_path", default="vault.db", show_default=True)
@click.option("--name", default=None, help="Show only this group.")
def list_cmd(vault_path: str, name: str | None) -> None:
    """List groups and their members."""
    if name:
        members = get_group(vault_path, name)
        if members:
            click.echo("\n".join(members))
        else:
            click.echo(f"Group '{name}' is empty or does not exist.")
    else:
        data = list_groups(vault_path)
        if not data:
            click.echo("No groups defined.")
        else:
            for g, keys in data.items():
                click.echo(f"{g}: {', '.join(keys)}")


@group.command("delete")
@click.argument("group_name")
@click.option("--vault", "vault_path", default="vault.db", show_default=True)
def delete_cmd(group_name: str, vault_path: str) -> None:
    """Delete an entire group."""
    if delete_group(vault_path, group_name):
        click.echo(f"Group '{group_name}' deleted.")
    else:
        click.echo(f"Group '{group_name}' does not exist.")
