"""CLI entry point for envault."""

import getpass
import sys
from pathlib import Path

import click

from envault.vault import Vault


def _get_vault(vault_file: str) -> Vault:
    return Vault(path=Path(vault_file))


@click.group()
@click.option("--vault", default=".envault.json", show_default=True, help="Path to vault file.")
@click.pass_context
def cli(ctx: click.Context, vault: str) -> None:
    """envault — securely manage environment secrets."""
    ctx.ensure_object(dict)
    ctx.obj["vault_path"] = vault


@cli.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx: click.Context, key: str, value: str) -> None:
    """Set a secret KEY to VALUE."""
    password = getpass.getpass("Vault password: ")
    vault = _get_vault(ctx.obj["vault_path"])
    vault.load(password)
    vault.set(key, value)
    vault.save(password)
    click.echo(f"Secret '{key}' saved.")


@cli.command()
@click.argument("key")
@click.pass_context
def get(ctx: click.Context, key: str) -> None:
    """Get the value of secret KEY."""
    password = getpass.getpass("Vault password: ")
    vault = _get_vault(ctx.obj["vault_path"])
    vault.load(password)
    try:
        click.echo(vault.get(key))
    except KeyError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


@cli.command(name="list")
@click.pass_context
def list_keys(ctx: click.Context) -> None:
    """List all secret keys in the vault."""
    password = getpass.getpass("Vault password: ")
    vault = _get_vault(ctx.obj["vault_path"])
    vault.load(password)
    keys = vault.list_keys()
    if not keys:
        click.echo("Vault is empty.")
    else:
        for k in keys:
            click.echo(k)


@cli.command()
@click.argument("key")
@click.pass_context
def delete(ctx: click.Context, key: str) -> None:
    """Delete secret KEY from the vault."""
    password = getpass.getpass("Vault password: ")
    vault = _get_vault(ctx.obj["vault_path"])
    vault.load(password)
    try:
        vault.delete(key)
        vault.save(password)
        click.echo(f"Secret '{key}' deleted.")
    except KeyError as e:
        click.echo(str(e), err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
