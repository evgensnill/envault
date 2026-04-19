"""CLI commands for env-check feature."""
from __future__ import annotations

import click

from envault.cli import _get_vault
from envault.env_check import check_env


@click.group("env-check")
def env_check():
    """Compare vault secrets against current environment variables."""


@env_check.command("run")
@click.argument("vault_path")
@click.argument("password")
@click.option("--key", "-k", multiple=True, help="Specific key(s) to check.")
@click.option("--strict", is_flag=True, default=False,
              help="Exit with non-zero status if any issue found.")
def run_cmd(vault_path: str, password: str, key: tuple, strict: bool):
    """Check environment variables against the vault."""
    vault = _get_vault(vault_path, password)
    keys = list(key) if key else None
    results = check_env(vault, keys=keys)

    issues = 0
    for r in results:
        if r.status == "ok":
            click.echo(click.style(f"  OK       {r.key}", fg="green"))
        elif r.status == "missing":
            click.echo(click.style(f"  MISSING  {r.key}", fg="yellow"))
            issues += 1
        else:
            click.echo(click.style(f"  MISMATCH {r.key}", fg="red"))
            issues += 1

    if issues:
        click.echo(f"\n{issues} issue(s) found.")
        if strict:
            raise SystemExit(1)
    else:
        click.echo("\nAll keys match.")
