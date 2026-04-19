"""CLI commands for vault snapshots."""
import click

from envault.cli import _get_vault
from envault.snapshot import delete_snapshot, list_snapshots, restore_snapshot, save_snapshot


@click.group("snapshot")
def snapshot():
    """Manage vault snapshots."""


@snapshot.command("save")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--label", default=None, help="Optional human-readable label.")
def save_cmd(vault_path, password, label):
    """Save a snapshot of the current vault state."""
    vault = _get_vault(vault_path, password)
    snap_id = save_snapshot(vault, label=label)
    click.echo(f"Snapshot saved: {snap_id}")


@snapshot.command("list")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def list_cmd(vault_path, password):
    """List available snapshots."""
    vault = _get_vault(vault_path, password)
    snaps = list_snapshots(vault)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        label = f"  [{s['label']}]" if s["label"] else ""
        click.echo(f"{s['snap_id']}{label}  (created_at={s['created_at']})")


@snapshot.command("restore")
@click.argument("snap_id")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--no-overwrite", is_flag=True, default=False)
def restore_cmd(vault_path, password, snap_id, no_overwrite):
    """Restore vault secrets from a snapshot."""
    vault = _get_vault(vault_path, password)
    restored = restore_snapshot(vault, snap_id, overwrite=not no_overwrite)
    click.echo(f"Restored {len(restored)} key(s): {', '.join(restored) or 'none'}")


@snapshot.command("delete")
@click.argument("snap_id")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def delete_cmd(vault_path, password, snap_id):
    """Delete a snapshot."""
    vault = _get_vault(vault_path, password)
    delete_snapshot(vault, snap_id)
    click.echo(f"Snapshot '{snap_id}' deleted.")
