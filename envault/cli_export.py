"""CLI commands for exporting vault secrets."""
from __future__ import annotations
import click

from envault.cli import _get_vault
from envault.export import export_vault, ExportFormat


@click.command("export")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["dotenv", "json", "shell"]),
    default="dotenv",
    show_default=True,
    help="Output format for exported secrets.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Write output to a file instead of stdout.",
)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def export(fmt: str, output: str | None, vault_path: str, password: str) -> None:
    """Export all secrets from the vault."""
    vault = _get_vault(vault_path, password)
    result = export_vault(vault, fmt=fmt)  # type: ignore[arg-type]

    if output:
        with open(output, "w") as fh:
            fh.write(result)
        click.echo(f"Exported to {output}")
    else:
        click.echo(result, nl=False)
