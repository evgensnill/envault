# Vault ↔ Environment Sync

The `sync` feature lets you push secrets from your vault into the current shell environment, pull environment variables back into the vault, and inspect differences between the two.

## Commands

### `envault sync push <vault> <password>`

Exports vault secrets as shell `export` statements. Pipe to `eval` to apply them:

```bash
eval "$(envault sync push .vault.enc mypassword)"
```

Options:
- `--key KEY` — push only the specified key (repeatable)
- `--no-overwrite` — skip keys that are already set in the environment

---

### `envault sync pull <vault> <password>`

Reads environment variables and writes them into the vault.

```bash
export NEW_SECRET=supersecret
envault sync pull .vault.enc mypassword --key NEW_SECRET
```

Options:
- `--key KEY` — pull only the specified key (repeatable; default: all vault keys)
- `--no-overwrite` — report conflicts instead of overwriting vault values

---

### `envault sync diff <vault> <password>`

Shows which vault keys differ from (or are absent in) the current environment.

```bash
envault sync diff .vault.enc mypassword
```

Output statuses:
- `missing_in_env` — key exists in vault but not in environment
- `changed` — key exists in both but values differ

---

## Programmatic API

```python
from envault.sync import push_to_env, pull_from_env, diff_with_env

result = push_to_env(vault, keys=["DB_URL"], overwrite=False)
print(result.pushed, result.skipped)

diffs = diff_with_env(vault)
for key, info in diffs.items():
    print(key, info["status"])
```
