"""CLI commands for key quality rating."""
from __future__ import annotations

import click
from envault.cli import _get_vault
from envault.rating import rate_vault, rate_key, save_rating


@click.group("rating")
def rating():
    """Assess and display key quality ratings."""


@rating.command("score")
@click.argument("vault_path")
@click.argument("password")
@click.argument("key", required=False)
@click.option("--save", "do_save", is_flag=True, default=False, help="Persist ratings.")
def score_cmd(vault_path: str, password: str, key: str | None, do_save: bool):
    """Show quality score(s). Pass KEY to score a single key."""
    vault = _get_vault(vault_path, password)
    if key:
        try:
            value = vault.get(key)
        except KeyError:
            raise click.ClickException(f"Key '{key}' not found.")
        result = rate_key(vault_path, key, value)
        results = [result]
    else:
        results = rate_vault(vault_path, vault)

    if not results:
        click.echo("No keys to rate.")
        return

    click.echo(f"{'KEY':<30} {'SCORE':>5}  {'GRADE':>5}  {'ENTROPY':>8}  {'LEN':>4}  {'FRESH':>5}")
    click.echo("-" * 65)
    for r in sorted(results, key=lambda x: x.score, reverse=True):
        len_flag = "ok" if r.length_ok else "low"
        fresh_flag = "ok" if r.freshness_ok else "old"
        click.echo(
            f"{r.key:<30} {r.score:>5}  {r.grade:>5}  {r.entropy_bits:>8.2f}  {len_flag:>4}  {fresh_flag:>5}"
        )
        if do_save:
            save_rating(vault_path, r)

    if do_save:
        click.echo("\nRatings saved.")


@rating.command("summary")
@click.argument("vault_path")
@click.argument("password")
def summary_cmd(vault_path: str, password: str):
    """Print grade distribution summary for the vault."""
    vault = _get_vault(vault_path, password)
    results = rate_vault(vault_path, vault)
    if not results:
        click.echo("No keys to rate.")
        return
    counts: dict[str, int] = {}
    for r in results:
        counts[r.grade] = counts.get(r.grade, 0) + 1
    avg = sum(r.score for r in results) / len(results)
    click.echo(f"Keys rated : {len(results)}")
    click.echo(f"Avg score  : {avg:.1f}")
    for grade in ("A", "B", "C", "D", "F"):
        click.echo(f"  {grade}: {counts.get(grade, 0)}")
