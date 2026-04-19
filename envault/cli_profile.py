"""CLI commands for profile management."""
import click
from envault import profile as prof


@click.group()
def profile():
    """Manage named vault profiles."""


@profile.command("add")
@click.argument("name")
@click.argument("vault_path")
@click.option("--description", "-d", default="", help="Optional description.")
def add_cmd(name: str, vault_path: str, description: str) -> None:
    """Add a new profile."""
    prof.add_profile(name, vault_path, description)
    click.echo(f"Profile '{name}' added.")


@profile.command("remove")
@click.argument("name")
def remove_cmd(name: str) -> None:
    """Remove a profile."""
    try:
        prof.remove_profile(name)
        click.echo(f"Profile '{name}' removed.")
    except KeyError as e:
        raise click.ClickException(str(e))


@profile.command("list")
def list_cmd() -> None:
    """List all profiles."""
    profiles = prof.list_profiles()
    default = prof.get_default_profile()
    if not profiles:
        click.echo("No profiles defined.")
        return
    for p in profiles:
        marker = " (default)" if p["name"] == default else ""
        desc = f"  # {p['description']}" if p.get("description") else ""
        click.echo(f"  {p['name']}{marker}: {p['vault_path']}{desc}")


@profile.command("use")
@click.argument("name")
def use_cmd(name: str) -> None:
    """Set the default profile."""
    try:
        prof.set_default_profile(name)
        click.echo(f"Default profile set to '{name}'.")
    except KeyError as e:
        raise click.ClickException(str(e))


@profile.command("show")
@click.argument("name")
def show_cmd(name: str) -> None:
    """Show details of a profile."""
    try:
        p = prof.get_profile(name)
        click.echo(f"Name:        {name}")
        click.echo(f"Vault path:  {p['vault_path']}")
        click.echo(f"Description: {p.get('description', '')}")
    except KeyError as e:
        raise click.ClickException(str(e))
