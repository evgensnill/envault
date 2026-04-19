"""CLI commands for vault diff."""
from __future__ import annotations

import click

from envault.cli import _get_vault
from envault.diff import diff_vaults, diff_vault_vs_env, DiffEntry
from envault.vault import Vault

_STATUS_COLORS = {
    "added": "green",
    "removed": "red",
    "changed": "yellow",
    "unchanged": "white",
}

_STATUS_SYMBOLS = {
    "added": "+",
    "removed": "-",
    "changed": "~",
    "unchanged": " ",
}


def _print_entries(entries: list[DiffEntry]) -> None:
    if not entries:
        click.echo("No differences found.")
        return
    for e in entries:
        sym = _STATUS_SYMBOLS[e.status]
        color = _STATUS_COLORS[e.status]
        if e.status == "added":
            line = f"{sym} {e.key}=(new) {e.new_value!r}"
        elif e.status == "removed":
            line = f"{sym} {e.key}={e.old_value!r} (removed)"
        elif e.status == "changed":
            line = f"{sym} {e.key}: {e.old_value!r} -> {e.new_value!r}"
        else:
            line = f"{sym} {e.key}={e.old_value!r}"
        click.echo(click.style(line, fg=color))


@click.command("diff")
@click.argument("vault_b_path")
@click.option("--password-a", prompt=True, hide_input=True, help="Password for current vault")
@click.option("--password-b", prompt=True, hide_input=True, help="Password for second vault")
@click.option("--show-unchanged", is_flag=True, default=False)
@click.pass_context
def diff(ctx: click.Context, vault_b_path: str, password_a: str, password_b: str, show_unchanged: bool) -> None:
    """Diff current vault against another vault file."""
    vault_a = _get_vault(ctx, password_a)
    vault_b = Vault(vault_b_path, password_b)
    vault_b.load()
    entries = diff_vaults(vault_a, vault_b, show_unchanged=show_unchanged)
    _print_entries(entries)


@click.command("diff-env")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True)
@click.option("--show-unchanged", is_flag=True, default=False)
@click.pass_context
def diff_env(ctx: click.Context, env_file: str, password: str, show_unchanged: bool) -> None:
    """Diff current vault against a .env file."""
    from envault.import_ import _parse_dotenv
    vault = _get_vault(ctx, password)
    with open(env_file) as fh:
        env_dict = _parse_dotenv(fh.read())
    entries = diff_vault_vs_env(vault, env_dict, show_unchanged=show_unchanged)
    _print_entries(entries)
