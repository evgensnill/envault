"""CLI commands for namespace management."""

from __future__ import annotations

import click

from envault.cli import _get_vault
from envault import namespace as ns_mod


@click.group("namespace")
def namespace() -> None:
    """Manage key namespaces."""


@namespace.command("assign")
@click.argument("key")
@click.argument("ns")
@click.option("--vault", "vault_path", required=True, envvar="ENVAULT_VAULT")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def assign_cmd(key: str, ns: str, vault_path: str, password: str) -> None:
    """Assign KEY to namespace NS."""
    _get_vault(vault_path, password)  # validate credentials
    try:
        ns_mod.assign_namespace(vault_path, key, ns)
        click.echo(f"Assigned '{key}' to namespace '{ns}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(str(exc))


@namespace.command("remove")
@click.argument("key")
@click.option("--vault", "vault_path", required=True, envvar="ENVAULT_VAULT")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def remove_cmd(key: str, vault_path: str, password: str) -> None:
    """Remove namespace assignment for KEY."""
    _get_vault(vault_path, password)
    removed = ns_mod.remove_namespace(vault_path, key)
    if removed:
        click.echo(f"Namespace assignment removed for '{key}'.")
    else:
        click.echo(f"'{key}' had no namespace assignment.")


@namespace.command("list")
@click.option("--vault", "vault_path", required=True, envvar="ENVAULT_VAULT")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
@click.option("--ns", "filter_ns", default=None, help="Filter by namespace name.")
def list_cmd(vault_path: str, password: str, filter_ns: str | None) -> None:
    """List namespace assignments."""
    _get_vault(vault_path, password)
    if filter_ns:
        keys = ns_mod.keys_in_namespace(vault_path, filter_ns)
        if keys:
            for k in sorted(keys):
                click.echo(f"  {k}")
        else:
            click.echo(f"No keys in namespace '{filter_ns}'.")
    else:
        mapping = ns_mod.list_namespaces(vault_path)
        if not mapping:
            click.echo("No namespace assignments.")
            return
        for name, keys in sorted(mapping.items()):
            click.echo(f"{name}:")
            for k in sorted(keys):
                click.echo(f"  {k}")
