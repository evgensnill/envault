"""CLI commands for policy management."""
import click
from envault.cli import _get_vault
from envault.policy import load_policy, save_policy, check_policy, PolicyRule


@click.group("policy")
def policy():
    """Manage vault key policies."""


@policy.command("check")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.password_option("--password", prompt=True, confirmation_prompt=False)
def check_cmd(vault_path, password):
    """Check vault against policy rules."""
    from pathlib import Path
    vault = _get_vault(vault_path, password)
    rules = load_policy(Path(vault_path))
    if not rules:
        click.echo("No policy file found.")
        return
    violations = check_policy(vault, rules)
    if not violations:
        click.secho("All policy checks passed.", fg="green")
    else:
        for v in violations:
            click.secho(f"[{v.rule}] {v.message}", fg="red")
        raise SystemExit(1)


@policy.command("add-rule")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--required", is_flag=True)
@click.option("--min-length", default=0, type=int)
@click.option("--pattern", default=None)
@click.option("--allowed-values", default=None, help="Comma-separated list")
def add_rule(key, vault_path, required, min_length, pattern, allowed_values):
    """Add or update a policy rule for KEY."""
    from pathlib import Path
    path = Path(vault_path)
    rules = load_policy(path)
    rules = [r for r in rules if r.key != key]
    rules.append(PolicyRule(
        key=key,
        required=required,
        min_length=min_length,
        pattern=pattern,
        allowed_values=[v.strip() for v in allowed_values.split(",")] if allowed_values else [],
    ))
    save_policy(path, rules)
    click.echo(f"Policy rule for {key!r} saved.")


@policy.command("list")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def list_rules(vault_path):
    """List all policy rules."""
    from pathlib import Path
    rules = load_policy(Path(vault_path))
    if not rules:
        click.echo("No rules defined.")
        return
    for r in rules:
        parts = [f"key={r.key}"]
        if r.required:
            parts.append("required")
        if r.min_length:
            parts.append(f"min_length={r.min_length}")
        if r.pattern:
            parts.append(f"pattern={r.pattern}")
        if r.allowed_values:
            parts.append(f"allowed={r.allowed_values}")
        click.echo("  ".join(parts))
