# Key Groups

envault lets you organise vault keys into named **groups** for easier bulk operations, documentation, and policy targeting.

## Concepts

- A **group** is a named collection of vault key names.
- Groups are stored in a sidecar file `<vault>.groups.json` next to the vault file.
- A key can belong to multiple groups simultaneously.
- Group names must be valid Python identifiers (letters, digits, underscores — no hyphens or spaces).

## CLI Usage

### Add a key to a group

```bash
envault group add database DB_HOST
envault group add database DB_PASS
```

### List all groups

```bash
envault group list
# database: DB_HOST, DB_PASS
# auth: API_KEY, SECRET
```

### List a specific group

```bash
envault group list --name database
# DB_HOST
# DB_PASS
```

### Remove a key from a group

```bash
envault group remove database DB_HOST
```

### Delete an entire group

```bash
envault group delete database
```

## Python API

```python
from envault.group import add_to_group, get_group, list_groups, delete_group

vault_path = "vault.db"
vault_keys = vault.list_keys()

add_to_group(vault_path, "database", "DB_HOST", vault_keys)
print(get_group(vault_path, "database"))   # ['DB_HOST']
print(list_groups(vault_path))             # {'database': ['DB_HOST']}
delete_group(vault_path, "database")
```

## Notes

- Groups do not affect encryption or secret storage — they are purely metadata.
- Deleting a key from the vault does **not** automatically remove it from groups; use `envault group remove` to keep groups consistent.
