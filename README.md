# envault

> CLI tool to securely manage and rotate environment secrets across multiple projects.

---

## Installation

```bash
pip install envault
```

Or with pipx (recommended):

```bash
pipx install envault
```

---

## Usage

Initialize a new vault in your project:

```bash
envault init
```

Add a secret:

```bash
envault set MY_API_KEY sk-abc123
```

Retrieve a secret:

```bash
envault get MY_API_KEY
```

Rotate secrets across projects:

```bash
envault rotate --project my-app --key DATABASE_URL
```

Export secrets to a `.env` file:

```bash
envault export > .env
```

Run a command with secrets injected into the environment:

```bash
envault run -- python app.py
```

---

## Features

- 🔐 AES-256 encrypted local vault
- 🔄 Secret rotation across multiple projects
- 📦 Simple CLI interface
- 🚀 Inject secrets directly into subprocesses

---

## License

MIT © [envault contributors](LICENSE)