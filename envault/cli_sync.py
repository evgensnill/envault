"""CLI commands for syncing vault secrets with the environment."""
from __future__ import annotations

import click

from envault.cli import _get_vault
from envault.sync import diff_with_env, pull_from_env, push_to_env


@click.group("sync")
def sync():
    """Sync secrets between vault and environment."""


@sync.command("push")
@click.argument("vault_path")
@click.argument("password")
@click.option("--key", "keys", multiple=True, help="Specific keys to push (default: all).")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys already in env.")
def push_cmd(vault_path: str, password: str, keys, no_overwrite: bool):
    """Push vault secrets into the current shell environment (exports to stdout)."""
    vault = _get_vault(vault_path, password)
    result = push_to_env(vault, list(keys) or None, overwrite=not no_overwrite)
    for key in result.pushed:
        click.echo(f"export {key}='{os.environ[key]}'")
    if result.skipped:
        click.echo(f"# Skipped: {', '.join(result.skipped)}", err=True)


@sync.command("pull")
@click.argument("vault_path")
@click.argument("password")
@click.option("--key", "keys", multiple=True, help="Specific env vars to pull (default: all vault keys).")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys already in vault.")
def pull_cmd(vault_path: str, password: str, keys, no_overwrite: bool):
    """Pull environment variables into the vault."""
    vault = _get_vault(vault_path, password)
    result = pull_from_env(vault, list(keys) or None, overwrite=not no_overwrite)
    click.echo(f"Pulled: {len(result.pulled)} key(s)")
    if result.conflicts:
        click.echo(f"Conflicts (skipped): {', '.join(result.conflicts)}", err=True)
    if result.skipped:
        click.echo(f"Skipped: {len(result.skipped)} key(s)")


@sync.command("diff")
@click.argument("vault_path")
@click.argument("password")
@click.option("--key", "keys", multiple=True, help="Specific keys to compare.")
def diff_cmd(vault_path: str, password: str, keys):
    """Show differences between vault and current environment."""
    vault = _get_vault(vault_path, password)
    diffs = diff_with_env(vault, list(keys) or None)
    if not diffs:
        click.echo("Vault and environment are in sync.")
        return
    for key, info in diffs.items():
        status = info["status"]
        if status == "missing_in_env":
            click.echo(f"  [missing_in_env] {key}")
        else:
            click.echo(f"  [changed]        {key}")


import os  # noqa: E402  (kept at bottom to avoid shadowing)
