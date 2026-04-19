# Policy Enforcement

envault supports defining per-vault policies to enforce constraints on secret keys.

## Policy File

Policies are stored in `.envault-policy.json` next to your vault file.

```json
{
  "rules": [
    {"key": "API_KEY", "required": true, "min_length": 16},
    {"key": "ENV", "allowed_values": ["prod", "staging"]},
    {"key": "PORT", "pattern": "\\d+"}
  ]
}
```

## Commands

### Add a rule

```bash
envault policy add-rule API_KEY --required --min-length 16
envault policy add-rule ENV --allowed-values prod,staging
envault policy add-rule PORT --pattern '\d+'
```

### List rules

```bash
envault policy list
```

### Check vault against policy

```bash
envault policy check
```

Exits with code 1 if any violations are found.

## Rule Options

| Option | Description |
|---|---|
| `--required` | Key must exist in the vault |
| `--min-length N` | Value must be at least N characters |
| `--pattern REGEX` | Value must fully match the regex |
| `--allowed-values a,b` | Value must be one of the listed options |

## Integration

Run `envault policy check` in CI to enforce secrets hygiene before deployment.
