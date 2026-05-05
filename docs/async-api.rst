Asynchronous API (AsyncOAuthToolkit)
=====================================

The ``AsyncOAuthToolkit`` class provides async OAuth/JWT operations for
modern async Python applications and async web frameworks.

.. _async-oauth-toolkit-class:

AsyncOAuthToolkit Class
-----------------------

.. autoclass:: oatk.async_toolkit.AsyncOAuthToolkit
   :members:
   :show-inheritance:
   :member-order: bysource

Key Differences from Sync API
------------------------------

The async API differs from the sync API in important ways:

1. **Async HTTP**: Uses ``httpx`` instead of ``requests``
2. **Async file I/O**: Uses ``anyio`` for non-blocking file operations
3. **Async provider init**: ``using_provider()`` and ``init_from_provider()`` are async
4. **Context-based auth**: Uses ``ContextVar`` for token management
5. **Framework-agnostic**: Decorators work with any async framework

Configuration Methods
---------------------

Loading Keys (Async)
~~~~~~~~~~~~~~~~~~~~

All file I/O operations are async:

.. code-block:: python

   from oatk import AsyncOAuthToolkit

   async def main():
       toolkit = AsyncOAuthToolkit()

       # Load private key (async)
       await toolkit.with_private("private_key.pem")

       # Load public key (async)
       await toolkit.with_public("public_key.pem")

       # Load JWKS from file (async)
       await toolkit.with_jwks("certs.json")

       # Load JWKS from string (sync)
       jwks_json = '{"keys": [...]}'
       await toolkit.with_jwks(jwks_json)  # Still async, but fast

Provider Configuration (Async)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure from an OAuth provider asynchronously:

.. code-block:: python

   async def main():
       toolkit = AsyncOAuthToolkit()

       # Fetch provider configuration
       await toolkit.using_provider(
           "https://accounts.google.com/.well-known/openid-configuration"
       )

       # Set client ID for audience validation
       toolkit.with_client_id("your-client-id")

**Error handling:**

.. code-block:: python

   try:
       result = await toolkit.using_provider(url)
       if result is None:
           print("Failed to initialize from provider")
   except Exception as e:
       print(f"Provider initialization failed: {e}")

**Manual initialization:**

.. code-block:: python

   toolkit._provider_url = "https://.../.well-known/openid-configuration"
   result = await toolkit.init_from_provider()

Token Operations
----------------

Creating Tokens
~~~~~~~~~~~~~~~

Token creation is synchronous (CPU-bound):

.. code-block:: python

   async def create_token():
       toolkit = AsyncOAuthToolkit()
       await toolkit.with_private("private_key.pem")

       # Set claims (sync)
       toolkit.claims(
           sub="user123",
           name="Alice",
           role="admin"
       )

       # Generate token (sync, CPU-bound)
       token = toolkit.token
       return token

**Note:** Token generation is synchronous because it's a CPU-bound
operation. The JWT encoding happens in memory without I/O.

Validating Tokens (Async)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Token validation is async to avoid blocking the event loop:

.. code-block:: python

   async def validate_token(token):
       toolkit = AsyncOAuthToolkit()
       await toolkit.with_public("public_key.pem")

       # Async validation
       claims = await toolkit.validate(token)
       return claims

**With provider:**

.. code-block:: python

   async def validate_google_token(token):
       toolkit = AsyncOAuthToolkit()
       await toolkit.using_provider(
           "https://accounts.google.com/.well-known/openid-configuration"
       )
       toolkit.with_client_id("your-client-id")

       claims = await toolkit.validate(token)
       return claims

**Error handling:**

.. code-block:: python

   from jwt import InvalidTokenError

   try:
       claims = await toolkit.validate(token)
   except InvalidTokenError as e:
       print(f"Invalid token: {e}")

Decoding Tokens
~~~~~~~~~~~~~~~

Decode without validation (synchronous, CPU-bound):

.. code-block:: python

   # Sync method - just decode, no I/O
   claims = toolkit.decode(token)

   # Or access header
   header = toolkit.header(token)

Token Loading (Async)
~~~~~~~~~~~~~~~~~~~~~

Load tokens asynchronously:

.. code-block:: python

   # From file (async)
   await toolkit.from_file("token.txt")

   # From clipboard (sync, no I/O)
   toolkit.from_clipboard()

   # Manual
   claims = await toolkit.validate(token_string)

JWKS Export
-----------

Export public key as JWKS (synchronous):

.. code-block:: python

   jwks = toolkit.jwks

   # Save to file
   async with await anyio.open_file("certs.json", "w") as f:
       await f.write(jwks)

Context-Based Authentication
-----------------------------

The async API uses Python's ``ContextVar`` for managing tokens across
async contexts.

Setting the Token
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Set token in current context
   AsyncOAuthToolkit.set_authorization_token(token)

   # Or extract from header
   token = toolkit.extract_token_from_header(auth_header)
   toolkit.set_authorization_token(token)

Getting the Token
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get token from current context
   token = AsyncOAuthToolkit.get_authorization_token()

   if token:
       claims = await toolkit.validate(token)

Framework-Agnostic Decorators
------------------------------

The async API provides decorators that work with any async framework.

Basic Authentication
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from oatk import AsyncOAuthToolkit

   toolkit = AsyncOAuthToolkit()
   await toolkit.with_public("public_key.pem")

   @toolkit.authenticated
   async def protected_route():
       return {"message": "authenticated"}

**Important:** You must set the token before calling the decorated function:

.. code-block:: python

   # In your framework's middleware or before calling:
   toolkit.set_authorization_token(token)
   result = await protected_route()

Claims-Based Authorization
~~~~~~~~~~~~~~~~~~~~~~~~~

Require specific claims:

.. code-block:: python

   @toolkit.authenticated_with_claims(role="admin")
   async def admin_route():
       return {"message": "admin only"}

   @toolkit.authenticated_with_claims(
       role="manager",
       department="engineering"
   )
   async def manager_route():
       return {"message": "engineering manager"}

**Custom validation:**

.. code-block:: python

   import time

   @toolkit.authenticated_with_claims(
       exp=lambda exp: exp > time.time()
   )
   async def valid_token_route():
       return {"message": "token not expired"}

How Decorators Work
~~~~~~~~~~~~~~~~~~~

The decorators use ``execute_authenticated()``:

.. code-block:: python

   async def protected_route():
       return {"message": "success"}

   # Manual authentication
   toolkit.set_authorization_token(token)
   result = await toolkit.execute_authenticated(
       protected_route,
       required_claims={"role": "admin"}
   )

**With framework integration:**

The decorators are framework-agnostic. Framework-specific integrations
(Quart, FastAPI) wrap these with automatic token extraction.

See :doc:`integrations` for framework-specific decorators.

Async with Quart
----------------

Use the Quart integration for automatic token extraction:

.. code-block:: python

   from quart import Quart
   from oatk import AsyncOAuthToolkit
   from oatk.quart import quart_authenticated

   app = Quart(__name__)
   toolkit = AsyncOAuthToolkit()

   @app.before_serving
   async def setup():
       await toolkit.using_provider("https://...")

   @app.route("/protected")
   @quart_authenticated(toolkit)
   async def protected():
       return {"message": "authenticated"}

See :doc:`integrations` for details.

Async with FastAPI
------------------

Use the FastAPI dependency injection:

.. code-block:: python

   from fastapi import FastAPI, Depends
   from oatk import AsyncOAuthToolkit
   from oatk.fastapi import OAuthToolkitDependency

   app = FastAPI()
   toolkit = AsyncOAuthToolkit()
   oauth = OAuthToolkitDependency(toolkit)

   @app.on_event("startup")
   async def startup():
       await toolkit.with_public("public_key.pem")

   @app.get("/protected")
   async def protected(user = Depends(oauth.get_current_user)):
       return {"user_id": user["sub"]}

See :doc:`integrations` for details.

Complete Async Example
----------------------

.. code-block:: python
   :caption: async_example.py

   import asyncio
   from oatk import AsyncOAuthToolkit

   async def main():
       # Initialize toolkit
       toolkit = AsyncOAuthToolkit()

       # Generate keys for demo
       from cryptography.hazmat.backends import default_backend
       from cryptography.hazmat.primitives.asymmetric import rsa

       private_key = rsa.generate_private_key(
           public_exponent=65537,
           key_size=2048,
           backend=default_backend()
       )

       toolkit._private_key = private_key
       toolkit._public_key = private_key.public_key()
       toolkit._certs = {toolkit._kid: toolkit._public_key}

       # Create token
       toolkit.claims(
           sub="user123",
           name="Alice",
           email="alice@example.com",
           role="admin"
       )
       token = toolkit.token
       print(f"Created token: {token[:50]}...")

       # Validate token
       claims = await toolkit.validate(token)
       print(f"Validated claims: {claims}")

       # Decode without validation
       decoded = toolkit.decode(token)
       print(f"Decoded claims: {decoded}")

       # Use with context
       toolkit.set_authorization_token(token)

       @toolkit.authenticated
       async def protected():
           return {"message": "authenticated"}

       result = await protected()
       print(f"Protected result: {result}")

   asyncio.run(main())

Async Best Practices
--------------------

**Use async context:**

.. code-block:: python

   # Good - all async operations
   async def setup():
       toolkit = AsyncOAuthToolkit()
       await toolkit.with_public("public_key.pem")
       await toolkit.using_provider("https://...")
       return toolkit

   # Bad - mixing sync and async unnecessarily
   async def bad_setup():
       toolkit = AsyncOAuthToolkit()
       toolkit.with_public("public_key.pem")  # Sync file I/O!
       await toolkit.using_provider("https://...")

**Handle CPU-bound operations:**

.. code-block:: python

   # Token creation is CPU-bound (sync)
   toolkit.claims(sub="user123")
   token = toolkit.token

   # Token validation is async (uses thread pool internally)
   claims = await toolkit.validate(token)

**Error handling:**

.. code-block:: python

   async def safe_validate(toolkit, token):
       try:
           return await toolkit.validate(token)
       except Exception as e:
           print(f"Validation failed: {e}")
           return None

Next Steps
----------

- Learn about :doc:`integrations` with Quart and FastAPI
- See :doc:`sync-api` for synchronous operations
- Read the :doc:`api-reference` for complete API details