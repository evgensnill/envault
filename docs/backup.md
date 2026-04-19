# Vault Backup & Restore

The `backup` command group lets you archive vault files and restore them when needed.

## Commands

### `envault backup create`

Create a compressed archive of a vault file.

```bash
envault backup create --vault .envault/vault.db --dest ./backups
envault backup create --vault .envault/vault.db --dest ./backups --label pre-deploy
```

The archive is stored as a `.tar.gz` file containing:
- The vault file itself
- A `backup_meta.json` with timestamp, label, and source path

### `envault backup list`

List all backups in a directory, newest first.

```bash
envault backup list --dest ./backups
```

Output example:
```
2024-06-01T12:00:00+00:00 [pre-deploy]  →  backups/backup_20240601T120000Z_pre-deploy.tar.gz
2024-05-30T08:00:00+00:00               →  backups/backup_20240530T080000Z.tar.gz
```

### `envault backup restore`

Restore a vault from an archive into a target directory.

```bash
envault backup restore backups/backup_20240601T120000Z.tar.gz --dest ./restored
```

Use `--overwrite` to replace an existing vault file:

```bash
envault backup restore backups/backup_20240601T120000Z.tar.gz --dest .envault --overwrite
```

## Notes

- Backups do **not** re-encrypt the vault; the vault file is already encrypted at rest.
- Combine with `envault snapshot` for in-place snapshots vs. off-directory archives.
- Automate backups via `envault hooks` on `post-set` events.
