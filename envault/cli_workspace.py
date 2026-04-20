"""CLI commands for workspace management."""

from __future__ import annotations

import click

from envault.workspace import (
    add_workspace,
    get_active_workspace,
    get_workspace,
    list_workspaces,
    remove_workspace,
    set_active_workspace,
)


@click.group("workspace")
def workspace() -> None:
    """Manage named workspaces (groups of vault paths)."""


@workspace.command("add")
@click.argument("name")
@click.argument("vault_path")
@click.option("--description", "-d", default="", help="Optional description.")
def add_cmd(name: str, vault_path: str, description: str) -> None:
    """Register a new workspace NAME pointing to VAULT_PATH."""
    add_workspace(name, vault_path, description)
    click.echo(f"Workspace '{name}' added → {vault_path}")


@workspace.command("remove")
@click.argument("name")
def remove_cmd(name: str) -> None:
    """Remove a workspace by NAME."""
    try:
        remove_workspace(name)
        click.echo(f"Workspace '{name}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@workspace.command("list")
def list_cmd() -> None:
    """List all registered workspaces."""
    names = list_workspaces()
    if not names:
        click.echo("No workspaces registered.")
        return
    active = get_active_workspace()
    for name in names:
        meta = get_workspace(name)
        marker = "*" if name == active else " "
        desc = f"  # {meta['description']}" if meta.get("description") else ""
        click.echo(f"  [{marker}] {name} → {meta['vault_path']}{desc}")


@workspace.command("use")
@click.argument("name")
def use_cmd(name: str) -> None:
    """Set NAME as the active workspace."""
    try:
        set_active_workspace(name)
        click.echo(f"Active workspace set to '{name}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@workspace.command("current")
def current_cmd() -> None:
    """Show the currently active workspace."""
    active = get_active_workspace()
    if active:
        meta = get_workspace(active)
        click.echo(f"{active} → {meta['vault_path']}")
    else:
        click.echo("No active workspace set.")
