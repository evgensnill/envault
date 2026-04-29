# Key Quality Rating

The `rating` module scores each secret in a vault on a 0–100 scale based on
three dimensions: **length**, **entropy**, and **freshness**.

## Scoring breakdown

| Dimension  | Max points | Notes                                         |
|------------|-----------|-----------------------------------------------|
| Length     | 40        | Full score at ≥ 32 characters                 |
| Entropy    | 40        | Full score at ≥ 5 bits/character              |
| Freshness  | 20        | Full score when rotated within the last 90 d  |

## Grades

| Score range | Grade |
|-------------|-------|
| 90 – 100    | A     |
| 75 – 89     | B     |
| 60 – 74     | C     |
| 40 – 59     | D     |
| 0  – 39     | F     |

## CLI usage

### Score a single key

```bash
envault rating score my.vault mypassword API_KEY
```

### Score all keys

```bash
envault rating score my.vault mypassword
```

Add `--save` to persist the ratings alongside the vault:

```bash
envault rating score my.vault mypassword --save
```

### Vault summary

```bash
envault rating summary my.vault mypassword
```

Outputs the grade distribution and average score across all keys.

## Programmatic API

```python
from envault.rating import rate_key, rate_vault, save_rating, get_saved_rating

# Rate a single key
result = rate_key(vault_path, key, value)
print(result.score, result.grade)

# Rate every key in an open vault
results = rate_vault(vault_path, vault)

# Persist and retrieve ratings
save_rating(vault_path, result)
record = get_saved_rating(vault_path, key)
```

Ratings are stored in a sidecar file `<vault>.ratings.json` next to the
vault file and are never encrypted — they contain no secret material.
