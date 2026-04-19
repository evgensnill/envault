"""CLI commands for vault sharing."""
from __future__ import annotations

import click

from envault.cli import _get_vault
from envault.sharing import export_bundle, import_bundle


@click.command("share-export")
@click.option("--vault-path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True, help="Master vault password")
@click.option(
    "--share-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Password to protect the shared bundle",
)
def share_export(vault_path: str, password: str, share_password: str) -> None:
    """Export an encrypted bundle that can be shared with another user."""
    vault = _get_vault(vault_path, password)
    bundle = export_bundle(vault, share_password)
    click.echo(bundle)


@click.command("share-import")
@click.argument("bundle")
@click.option("--vault-path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True, help="Master vault password")
@click.option(
    "--share-password",
    prompt=True,
    hide_input=True,
    help="Password used when the bundle was created",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys",
)
def share_import(
    bundle: str, vault_path: str, password: str, share_password: str, overwrite: bool
) -> None:
    """Import secrets from an encrypted bundle into the vault."""
    vault = _get_vault(vault_path, password)
    try:
        imported = import_bundle(vault, bundle, share_password, overwrite=overwrite)
    except Exception as exc:
        raise click.ClickException(str(exc))
    if imported:
        click.echo(f"Imported {len(imported)} key(s): {', '.join(imported)}")
    else:
        click.echo("No new keys imported (use --overwrite to replace existing keys).")
