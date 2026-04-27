# Webhook Notifications

envault can notify external services when vault events occur via HTTP webhooks.

## Supported Events

| Event | Triggered when |
|-------|----------------|
| `set` | A key is created or updated |
| `rotate` | A key value is rotated |
| `delete` | A key is removed |
| `import` | Secrets are imported |
| `restore` | A snapshot or backup is restored |
| `expire` | A key's TTL expires |

## Managing Webhooks

### Register a webhook

```bash
envault webhook add slack https://hooks.slack.com/services/XXX --events set,rotate
```

Optionally include a shared secret for request verification:

```bash
envault webhook add deploy https://ci.example.com/hook --events rotate --secret mysecret
```

The secret is sent as the `X-Envault-Secret` HTTP header.

### List registered webhooks

```bash
envault webhook list
```

### Remove a webhook

```bash
envault webhook remove slack
```

### Manually fire an event

Useful for testing your endpoint:

```bash
envault webhook fire set --key MY_API_KEY
```

## Payload Format

All requests are HTTP POST with `Content-Type: application/json`:

```json
{
  "event": "rotate",
  "timestamp": 1712345678.123,
  "payload": {
    "key": "MY_API_KEY"
  }
}
```

## Integration with Hooks

Webhooks complement the local `hooks` system. Use hooks for local scripts and
webhooks for remote HTTP notifications.
