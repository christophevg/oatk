# oatk - OAuth Toolkit

[![Latest Version on PyPI](https://img.shields.io/pypi/v/oatk.svg)](https://pypi.python.org/pypi/oatk/)
[![PyPI downloads](https://img.shields.io/pypi/dm/oatk.svg)](https://pypistats.org/packages/oatk)
[![Supported Implementations](https://img.shields.io/pypi/pyversions/oatk.svg)](https://pypi.python.org/pypi/oatk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/christophevg/oatk/actions/workflows/test.yml/badge.svg)](https://github.com/christophevg/oatk/actions/workflows/test.yml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-7c85a3.svg)](https://docs.astral.sh/ruff/)

A clean, simple Python OAuth toolkit for quick prototypes and learning. Provides both synchronous and asynchronous implementations with framework integrations for Flask, Quart, and FastAPI.

## Quick Start

### Installation

```bash
pip install oatk
```

For async support:
```bash
pip install oatk[async]
```

For framework integrations:
```bash
pip install oatk[quart]      # Quart (async Flask)
pip install oatk[fastapi]    # FastAPI
```

### Basic Usage (Synchronous)

```python
from oatk import OAuthToolkit

# Create and validate tokens
toolkit = OAuthToolkit()
toolkit.with_private("private_key.pem")
toolkit.with_public("public_key.pem")

# Create a token
toolkit.claims(user="alice", role="admin")
token = toolkit.token

# Validate a token
claims = toolkit.validate(token)
print(claims)  # {'user': 'alice', 'role': 'admin'}
```

### Basic Usage (Asynchronous)

```python
from oatk import AsyncOAuthToolkit

async def main():
    toolkit = AsyncOAuthToolkit()

    # Configure from OAuth provider
    await toolkit.using_provider(
        "https://accounts.google.com/.well-known/openid-configuration"
    )

    # Validate token
    claims = await toolkit.validate(token)
    print(claims)

# Or use with async context
async with AsyncOAuthToolkit() as toolkit:
    await toolkit.with_public("public_key.pem")
    claims = await toolkit.validate(token)
```

### Flask Integration

```python
from flask import Flask
from oatk import OAuthToolkit

app = Flask(__name__)
toolkit = OAuthToolkit()
toolkit.with_jwks("certs.json")

@app.route("/protected")
@toolkit.authenticated
def protected():
    return {"message": "authenticated"}

@app.route("/admin")
@toolkit.authenticated_with_claims(role="admin")
def admin():
    return {"message": "admin only"}
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from oatk.async_toolkit import AsyncOAuthToolkit
from oatk.fastapi import OAuthToolkitDependency

app = FastAPI()
toolkit = AsyncOAuthToolkit()
oauth = OAuthToolkitDependency(toolkit)

@app.get("/protected")
async def protected(user = Depends(oauth.get_current_user)):
    return {"user_id": user["sub"]}

@app.get("/admin")
async def admin(user = Depends(oauth.require_claims(role="admin"))):
    return {"message": "admin access"}
```

## Features

### Core Features
- Token creation with RSA private keys
- Token validation with RSA public keys
- JWKS import/export for key distribution
- Provider-based configuration (OpenID Connect)
- Token decoding (without validation)

### Synchronous API (OAuthToolkit)
- Flask route decorators (`@authenticated`, `@authenticated_with_claims`)
- Command-line interface for quick operations
- Clipboard support (macOS)

### Asynchronous API (AsyncOAuthToolkit)
- Async HTTP operations with httpx
- Async file I/O with anyio
- Framework-agnostic decorators
- Context-based token management

### Framework Integrations
- **Flask** (sync): Route decorators for authentication
- **Quart** (async): Automatic token extraction from requests
- **FastAPI** (async): Dependency injection pattern

## Command Line Interface

Generate a JWKS from a public key:
```bash
oatk with_public public_key.pem jwks
```

Create a token:
```bash
oatk with_private private_key.pem with_jwks certs.json claims '{"user":"alice"}' token
```

Validate a token:
```bash
oatk with_jwks certs.json from_file token.txt validate
```

Decode a token (without validation):
```bash
oatk from_file token.txt decode
```

## Running Examples

The repository includes example applications demonstrating framework integrations. Use the Makefile targets to run them:

### Quart Example (Async Flask)

```bash
make quart-example
```

This runs the Quart async OAuth example with auto-reload enabled. See `examples/quart_example.py`.

### FastAPI Example

```bash
make fastapi-example
```

This runs the FastAPI async OAuth example with auto-reload enabled. See `examples/fastapi_example.py`.

Both examples demonstrate:
- OAuth toolkit initialization and configuration
- Token validation in route decorators
- Role-based access control
- Claim-based authorization

## Documentation

Full documentation is available at: https://oatk.readthedocs.io

- [Installation Guide](docs/installation.rst)
- [Quick Start Tutorial](docs/quickstart.rst)
- [Sync API Reference](docs/sync-api.rst)
- [Async API Reference](docs/async-api.rst)
- [Framework Integrations](docs/integrations.rst)
- [API Reference](docs/api-reference.rst)

## Use Cases

oatk is designed for:

- **Quick prototypes**: Get OAuth up and running in minutes
- **Learning**: Understand OAuth/JWT concepts with clean, readable code
- **Development environments**: Test OAuth flows without complex setup
- **Understanding**: See what's happening under the hood

For production systems, consider battle-tested alternatives like Authlib, python-jose, or similar.

## Security Disclaimer

This software deals with authentication and authorization, which are critical security components. All software can contain bugs, including security vulnerabilities.

By using this software, you acknowledge that:
- You understand the security implications
- You take responsibility for any security-related issues
- This toolkit is designed primarily for prototypes and learning
- For production systems, consider battle-tested alternatives like Authlib, python-jose, or similar

USE AT YOUR OWN RISK. The authors and contributors are not responsible for any security breaches, data loss, or other damages resulting from the use of this software.

## Requirements

- Python 3.9+
- RSA key pair (for token signing/validation)

Generate keys:
```bash
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem
```

## License

MIT License - see [LICENSE.txt](LICENSE.txt)

## Links

- [PyPI](https://pypi.python.org/pypi/oatk/)
- [GitHub](https://github.com/christophevg/oatk)
- [Documentation](https://oatk.readthedocs.io)
- [Issue Tracker](https://github.com/christophevg/oatk/issues)