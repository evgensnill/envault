"""CLI commands for managing webhooks."""
import click
from envault.cli import _get_vault
from envault import webhook as wh


@click.group("webhook")
def webhook():
    """Manage webhook notifications."""


@webhook.command("add")
@click.argument("name")
@click.argument("url")
@click.option("--events", required=True, help="Comma-separated list of events.")
@click.option("--secret", default="", help="Optional shared secret sent in X-Envault-Secret header.")
@click.pass_context
def add_cmd(ctx, name, url, events, secret):
    """Register a webhook endpoint."""
    vault = _get_vault(ctx)
    event_list = [e.strip() for e in events.split(",") if e.strip()]
    try:
        entry = wh.add_webhook(vault.path, name, url, event_list, secret)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Webhook '{name}' registered for events: {', '.join(entry.events)}")


@webhook.command("remove")
@click.argument("name")
@click.pass_context
def remove_cmd(ctx, name):
    """Remove a registered webhook."""
    vault = _get_vault(ctx)
    removed = wh.remove_webhook(vault.path, name)
    if removed:
        click.echo(f"Webhook '{name}' removed.")
    else:
        raise click.ClickException(f"No webhook named '{name}'.")


@webhook.command("list")
@click.pass_context
def list_cmd(ctx):
    """List all registered webhooks."""
    vault = _get_vault(ctx)
    entries = wh.list_webhooks(vault.path)
    if not entries:
        click.echo("No webhooks registered.")
        return
    for name, entry in entries.items():
        status = "enabled" if entry.enabled else "disabled"
        click.echo(f"{name}  {entry.url}  events=[{', '.join(entry.events)}]  {status}")


@webhook.command("fire")
@click.argument("event")
@click.option("--key", default="", help="Optional key name to include in payload.")
@click.pass_context
def fire_cmd(ctx, event, key):
    """Manually fire an event to all matching webhooks."""
    vault = _get_vault(ctx)
    payload = {"key": key} if key else {}
    results = wh.fire_event(vault.path, event, payload)
    if not results:
        click.echo("No webhooks matched.")
        return
    for name, success in results.items():
        status = "OK" if success else "FAILED"
        click.echo(f"  {name}: {status}")
