"""CLI commands for rotation reminders."""
import click
from envault.cli import _get_vault
from envault.remind import check_reminders, overdue_keys


@click.group()
def remind():
    """Rotation reminder commands."""


@remind.command("check")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--max-age", default=90, show_default=True, help="Max age in days.")
@click.option("--key", "keys", multiple=True, help="Limit to specific keys.")
def check_cmd(vault_path, password, max_age, keys):
    """Show rotation status for all (or selected) keys."""
    vault = _get_vault(vault_path, password)
    entries = check_reminders(vault, max_age_days=max_age, keys=list(keys) or None)
    if not entries:
        click.echo("No keys found.")
        return
    for e in entries:
        status = click.style("OVERDUE", fg="red") if e.overdue else click.style("OK", fg="green")
        rotated = e.last_rotated.strftime("%Y-%m-%d") if e.last_rotated else "never"
        due_str = f"{abs(e.due_in)}d overdue" if e.overdue else f"due in {e.due_in}d"
        click.echo(f"  [{status}] {e.key:30s}  last rotated: {rotated:12s}  ({due_str})")


@remind.command("overdue")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--max-age", default=90, show_default=True, help="Max age in days.")
def overdue_cmd(vault_path, password, max_age):
    """List only overdue keys (exits non-zero if any found)."""
    vault = _get_vault(vault_path, password)
    keys = overdue_keys(vault, max_age_days=max_age)
    if not keys:
        click.echo("All keys are within rotation policy.")
        return
    click.echo(click.style(f"{len(keys)} overdue key(s):", fg="red"))
    for k in keys:
        click.echo(f"  - {k}")
    raise SystemExit(1)
