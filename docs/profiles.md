# Profiles

Envault profiles let you manage multiple named vault configurations, making it easy to switch between environments (dev, staging, production).

## Concepts

A **profile** stores:
- `name` — unique identifier
- `vault_path` — path to the `.vault` file
- `description` — optional human-readable note

One profile may be marked as the **default**, used when no explicit path is given.

## Commands

### Add a profile

```bash
envault profile add dev /path/to/dev.vault --description "Development secrets"
```

### List profiles

```bash
envault profile list
```

The default profile is marked with `(default)`.

### Set default profile

```bash
envault profile use dev
```

### Show profile details

```bash
envault profile show dev
```

### Remove a profile

```bash
envault profile remove dev
```

## Storage

Profiles are stored in `~/.envault/profiles.json`. This file is local to your machine and should not be committed to version control.

## Example workflow

```bash
# Set up profiles for each environment
envault profile add dev ./dev.vault
envault profile add prod ./prod.vault --description "Production — handle with care"

# Work with dev by default
envault profile use dev

# Inspect a specific profile
envault profile show prod
```
