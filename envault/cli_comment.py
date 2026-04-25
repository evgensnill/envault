"""CLI commands for managing per-key comments."""

from __future__ import annotations

import click

from envault.cli import _get_vault
from envault import comment as comment_mod


@click.group("comment")
def comment():
    """Manage key comments and annotations."""


@comment.command("set")
@click.argument("vault_path")
@click.argument("key")
@click.argument("text")
@click.option("--password", prompt=True, hide_input=True)
def set_cmd(vault_path: str, key: str, text: str, password: str) -> None:
    """Set a comment for a vault key."""
    vault = _get_vault(vault_path, password)
    try:
        comment_mod.set_comment(vault_path, key, text, vault=vault)
        click.echo(f"Comment set for '{key}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))


@comment.command("get")
@click.argument("vault_path")
@click.argument("key")
def get_cmd(vault_path: str, key: str) -> None:
    """Get the comment for a vault key."""
    value = comment_mod.get_comment(vault_path, key)
    if value is None:
        click.echo(f"No comment set for '{key}'.")
    else:
        click.echo(value)


@comment.command("remove")
@click.argument("vault_path")
@click.argument("key")
def remove_cmd(vault_path: str, key: str) -> None:
    """Remove the comment for a vault key."""
    removed = comment_mod.remove_comment(vault_path, key)
    if removed:
        click.echo(f"Comment removed for '{key}'.")
    else:
        click.echo(f"No comment found for '{key}'.")


@comment.command("list")
@click.argument("vault_path")
def list_cmd(vault_path: str) -> None:
    """List all key comments."""
    entries = comment_mod.list_comments(vault_path)
    if not entries:
        click.echo("No comments recorded.")
        return
    for key, text in sorted(entries.items()):
        click.echo(f"{key}: {text}")
