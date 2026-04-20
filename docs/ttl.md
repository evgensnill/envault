# Secret TTL (Time-to-Live)

envault lets you attach a **time-to-live** to any secret so you always know
when credentials have expired and need rotation.

## Concepts

| Term | Meaning |
|------|---------|
| TTL | Duration in seconds before a secret is considered expired |
| `expires_at` | Unix timestamp computed as `now + ttl_seconds` at the time `set` is called |
| Expired | A secret whose `expires_at` is in the past |

TTL metadata is stored in a sidecar file (`.envault_ttl.json`) next to the
vault file and is **not encrypted** — it only contains timestamps, not secret
values.

## CLI Usage

### Set a TTL

```bash
# Expire API_KEY in 30 days (2 592 000 seconds)
envault ttl set API_KEY 2592000 --vault prod.db
```

### Inspect a key's TTL

```bash
envault ttl get API_KEY --vault prod.db
# Key: API_KEY  TTL: 2592000s  Status: 2591823s remaining
```

### List all TTLs

```bash
envault ttl list --vault prod.db
```

### Find expired secrets

```bash
envault ttl expired --vault prod.db
```

Combine with `envault rotate` to automate credential rotation:

```bash
for key in $(envault ttl expired --vault prod.db); do
  envault rotate "$key" --vault prod.db
done
```

### Remove a TTL

```bash
envault ttl remove API_KEY --vault prod.db
```

## Python API

```python
from envault import ttl

ttl.set_ttl("prod.db", "DB_PASS", seconds=86400)   # 1 day
print(ttl.is_expired("prod.db", "DB_PASS"))         # False (just set)
print(ttl.expired_keys("prod.db", ["DB_PASS", "TOKEN"]))  # []
```
