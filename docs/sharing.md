# Vault Sharing

envault supports securely sharing secrets between team members or machines via
an encrypted, self-contained **bundle**.

## How It Works

1. The exporting user serialises all plaintext secrets into JSON.
2. The JSON is encrypted with a *share password* (independent of the vault
   master password) using the same AES-based scheme as the vault itself.
3. The resulting ciphertext is base64-encoded and printed to stdout.
4. The receiving user pastes the bundle string into `share-import`, supplies
   the share password, and the secrets are decrypted and written into their
   local vault.

## Commands

### Export

```bash
envault share-export --vault-path .envault
# prompts: master password, share password (confirmed)
# prints:  <base64-bundle>
```

### Import

```bash
envault share-import <base64-bundle> --vault-path .envault
# prompts: master password, share password
```

Use `--overwrite` to replace keys that already exist in the destination vault:

```bash
envault share-import <bundle> --overwrite
```

## Security Notes

- The share password is **not** stored anywhere; both parties must exchange it
  out-of-band (e.g. via a secure channel).
- The bundle is safe to transmit over untrusted channels because it is
  encrypted before encoding.
- Each export uses a fresh random salt, so two exports of the same vault with
  the same password produce different bundles.
