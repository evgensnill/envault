"""CLI commands for managing favorite keys."""
from __future__ import annotations

import click

from envault.cli import _get_vault
from envault.favorite import (
    add_favorite,
    clear_favorites,
    is_favorite,
    list_favorites,
    remove_favorite,
)


@click.group("favorite")
def favorite():
    """Mark vault keys as favorites for quick access."""


@favorite.command("add")
@click.argument("vault_path")
@click.argument("key")
@click.password_option("--password", prompt="Vault password")
def add_cmd(vault_path: str, key: str, password: str) -> None:
    """Mark KEY as a favorite."""
    vault = _get_vault(vault_path, password)
    try:
        add_favorite(vault_path, key, vault)
        click.echo(f"Added '{key}' to favorites.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@favorite.command("remove")
@click.argument("vault_path")
@click.argument("key")
def remove_cmd(vault_path: str, key: str) -> None:
    """Remove KEY from favorites."""
    removed = remove_favorite(vault_path, key)
    if removed:
        click.echo(f"Removed '{key}' from favorites.")
    else:
        click.echo(f"'{key}' was not in favorites.")


@favorite.command("list")
@click.argument("vault_path")
def list_cmd(vault_path: str) -> None:
    """List all favorite keys."""
    favs = list_favorites(vault_path)
    if not favs:
        click.echo("No favorites set.")
    else:
        for key in favs:
            click.echo(key)


@favorite.command("clear")
@click.argument("vault_path")
@click.confirmation_option(prompt="Clear all favorites?")
def clear_cmd(vault_path: str) -> None:
    """Remove all favorites."""
    count = clear_favorites(vault_path)
    click.echo(f"Cleared {count} favorite(s).")
