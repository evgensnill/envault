"""CLI commands for secret rotation."""
import click
from envault.cli import cli, _get_vault
from envault.rotation import rotate_key, last_rotated, keys_older_than


@cli.command("rotate")
@click.argument("key")
@click.argument("new_value")
@click.option("--vault-path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def rotate(key: str, new_value: str, vault_path: str, password: str) -> None:
    """Rotate KEY to NEW_VALUE and record the rotation time."""
    vault = _get_vault(vault_path, password)
    rotate_key(vault, key, new_value)
    click.echo(f"Rotated '{key}' successfully.")


@cli.command("rotation-info")
@click.argument("key")
@click.option("--vault-path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def rotation_info(key: str, vault_path: str, password: str) -> None:
    """Show when KEY was last rotated."""
    vault = _get_vault(vault_path, password)
    ts = last_rotated(vault, key)
    if ts is None:
        click.echo(f"No rotation record found for '{key}'.")
    else:
        click.echo(f"'{key}' last rotated at {ts.isoformat()} UTC")


@cli.command("stale-keys")
@click.option("--days", default=90, show_default=True, help="Rotation age threshold in days.")
@click.option("--vault-path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def stale_keys(days: int, vault_path: str, password: str) -> None:
    """List keys not rotated within DAYS days."""
    vault = _get_vault(vault_path, password)
    stale = keys_older_than(vault, days)
    if not stale:
        click.echo(f"All keys rotated within the last {days} days.")
    else:
        click.echo(f"Stale keys (older than {days} days):")
        for k in stale:
            click.echo(f"  - {k}")
