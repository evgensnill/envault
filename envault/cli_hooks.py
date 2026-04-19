"""CLI commands for managing envault hooks."""
from __future__ import annotations

import click
from pathlib import Path

from envault.hooks import add_hook, remove_hook, load_hooks, run_hooks, _VALID_EVENTS


@click.group("hooks")
def hooks():
    """Manage pre/post operation hooks."""


@hooks.command("add")
@click.argument("event")
@click.argument("command")
@click.option("--vault", default="vault.db", show_default=True)
def add_cmd(event: str, command: str, vault: str) -> None:
    """Register COMMAND to run on EVENT."""
    try:
        add_hook(Path(vault), event, command)
        click.echo(f"Hook added: [{event}] {command}")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@hooks.command("remove")
@click.argument("event")
@click.argument("command")
@click.option("--vault", default="vault.db", show_default=True)
def remove_cmd(event: str, command: str, vault: str) -> None:
    """Remove COMMAND from EVENT hooks."""
    removed = remove_hook(Path(vault), event, command)
    if removed:
        click.echo(f"Hook removed: [{event}] {command}")
    else:
        click.echo(f"Hook not found: [{event}] {command}")


@hooks.command("list")
@click.option("--vault", default="vault.db", show_default=True)
def list_cmd(vault: str) -> None:
    """List all registered hooks."""
    all_hooks = load_hooks(Path(vault))
    if not all_hooks:
        click.echo("No hooks registered.")
        return
    for event, cmds in sorted(all_hooks.items()):
        for cmd in cmds:
            click.echo(f"  {event}: {cmd}")


@hooks.command("run")
@click.argument("event")
@click.option("--vault", default="vault.db", show_default=True)
def run_cmd(event: str, vault: str) -> None:
    """Manually trigger hooks for EVENT."""
    outputs = run_hooks(Path(vault), event)
    if not outputs:
        click.echo(f"No hooks for event '{event}'.")
    for out in outputs:
        if out:
            click.echo(out)
