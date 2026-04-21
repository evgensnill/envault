"""CLI commands for managing key dependencies."""
import click
from envault.cli import _get_vault
from envault import dependency


@click.group("dependency")
def dep():
    """Manage dependencies between vault keys."""


@dep.command("add")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault", "vault_path", required=True, envvar="ENVAULT_VAULT", help="Path to vault file")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def add_cmd(key, depends_on, vault_path, password):
    """Add a dependency: KEY depends on DEPENDS_ON."""
    v = _get_vault(vault_path, password)
    try:
        dependency.add_dependency(vault_path, key, depends_on, v)
        click.echo(f"Added: '{key}' depends on '{depends_on}'")
    except (KeyError, ValueError) as exc:
        raise click.ClickException(str(exc))


@dep.command("remove")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault", "vault_path", required=True, envvar="ENVAULT_VAULT")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
def remove_cmd(key, depends_on, vault_path, password):
    """Remove a dependency between KEY and DEPENDS_ON."""
    _get_vault(vault_path, password)
    removed = dependency.remove_dependency(vault_path, key, depends_on)
    if removed:
        click.echo(f"Removed: '{key}' no longer depends on '{depends_on}'")
    else:
        click.echo(f"No such dependency: '{key}' -> '{depends_on}'")


@dep.command("list")
@click.argument("key")
@click.option("--vault", "vault_path", required=True, envvar="ENVAULT_VAULT")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD")
@click.option("--reverse", is_flag=True, help="Show keys that depend on KEY instead")
def list_cmd(key, vault_path, password, reverse):
    """List dependencies for KEY."""
    _get_vault(vault_path, password)
    if reverse:
        items = dependency.get_dependents(vault_path, key)
        label = f"Keys that depend on '{key}'"
    else:
        items = dependency.get_dependencies(vault_path, key)
        label = f"'{key}' depends on"
    if not items:
        click.echo(f"{label}: (none)")
    else:
        click.echo(f"{label}:")
        for item in items:
            click.echo(f"  - {item}")
