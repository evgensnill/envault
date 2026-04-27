# Vault Quota Management

envault supports optional key quotas to prevent vaults from growing beyond a
configured size. This is useful when enforcing discipline in large teams or
when a downstream system has a hard limit on the number of environment
variables it accepts.

## Setting a Quota

```bash
envault quota set path/to/vault.enc 50
```

This limits the vault to **50 keys**. Attempting to add more keys when the
limit is reached will raise an error (if enforcement is wired into your `set`
workflow via `enforce_quota`).

## Checking the Current Quota

```bash
envault quota get path/to/vault.enc
# Quota limit: 50 keys
```

If no quota is configured:

```bash
# No quota configured.
```

## Inspecting Usage

```bash
envault quota check path/to/vault.enc
# Keys: 23/50 (remaining: 27)
```

If the vault already exceeds its quota (e.g. after the limit was lowered), the
command exits with code **2** and prints a warning.

## Removing a Quota

```bash
envault quota remove path/to/vault.enc
# Quota removed.
```

## Python API

```python
from envault.quota import set_quota, get_quota, check_quota, enforce_quota

# Configure
set_quota("vault.enc", 100)

# Read
limit = get_quota("vault.enc")  # 100

# Inspect usage (raises QuotaExceededError if over limit)
info = check_quota("vault.enc", vault)
print(info.current, info.limit, info.remaining)

# Call before writing a new key
enforce_quota("vault.enc", vault)  # raises if at/over limit
```

## Error Handling

| Exception | Meaning |
|---|---|
| `QuotaExceededError` | Vault is at or over its key limit |
| `ValueError` | Invalid limit value or no quota configured |
