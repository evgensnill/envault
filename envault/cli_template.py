"""CLI commands for template rendering."""
from __future__ import annotations

from pathlib import Path

import click

from envault.cli import _get_vault
from envault.template import render_file, render_string


@click.group("template")
def template():
    """Render templates using vault secrets."""


@template.command("render")
@click.argument("template_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path), default=None,
              help="Write rendered output to this file (default: stdout).")
@click.option("--vault", "vault_path", default=".envault",
              show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
def render(template_file: Path, output: Path | None, vault_path: str, password: str):
    """Render TEMPLATE_FILE substituting {{KEY}} with vault values."""
    vault = _get_vault(vault_path, password)
    rendered, missing = render_file(template_file, vault, dest=output)
    if missing:
        click.secho(f"Warning: unresolved placeholders: {', '.join(missing)}",
                    fg="yellow", err=True)
    if output is None:
        click.echo(rendered, nl=False)
    else:
        click.secho(f"Rendered to {output}", fg="green")


@template.command("check")
@click.argument("template_file", type=click.Path(exists=True, path_type=Path))
@click.option("--vault", "vault_path", default=".envault",
              show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
def check(template_file: Path, vault_path: str, password: str):
    """Check TEMPLATE_FILE for placeholders missing from the vault."""
    vault = _get_vault(vault_path, password)
    text = template_file.read_text(encoding="utf-8")
    _, missing = render_string(text, vault)
    if missing:
        click.secho("Missing keys:", fg="red")
        for k in missing:
            click.echo(f"  - {k}")
        raise SystemExit(1)
    click.secho("All placeholders resolved.", fg="green")
