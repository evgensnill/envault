# Secret Rotation

envault tracks when each secret was last rotated so you can enforce rotation policies.

## Commands

### `envault rotate KEY NEW_VALUE`

Update `KEY` to `NEW_VALUE` and record the rotation timestamp.

```bash
envault rotate DB_PASSWORD s3cr3t-new --vault-path .envault
```

### `envault rotation-info KEY`

Display when `KEY` was last rotated.

```bash
envault rotation-info DB_PASSWORD
# 'DB_PASSWORD' last rotated at 2024-05-01T12:34:56 UTC
```

### `envault stale-keys --days N`

List all keys whose last rotation is older than `N` days (default: 90).

```bash
envault stale-keys --days 30
```

## How It Works

Rotation metadata is stored as a JSON blob under a reserved key (`__rotation_meta__`) inside the vault itself, so it is encrypted alongside your secrets.

Each entry maps a secret key name to an ISO-8601 UTC timestamp of its last rotation.

## Programmatic Usage

```python
from envault.rotation import rotate_key, last_rotated, keys_older_than

rotate_key(vault, "API_TOKEN", "new-token-value")
print(last_rotated(vault, "API_TOKEN"))
stale = keys_older_than(vault, days=90)
```
