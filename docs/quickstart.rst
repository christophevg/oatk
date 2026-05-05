Quick Start
===========

This guide will help you get started with oatk in 5 minutes.

Prerequisites
-------------

Before starting, ensure you have:

1. Python 3.9 or higher installed
2. An RSA key pair (see :doc:`installation`)

Generate keys if you haven't already:

.. code-block:: bash

   openssl genrsa -out private_key.pem 2048
   openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem

Basic Workflow
--------------

The typical oatk workflow is:

1. **Configure** the toolkit with your keys
2. **Create** tokens (with private key)
3. **Distribute** public keys via JWKS
4. **Validate** tokens (with public key)

Synchronous Example
-------------------

Create a file ``quickstart.py``:

.. code-block:: python
   :caption: quickstart.py

   from oatk import OAuthToolkit

   # 1. Configure the toolkit
   toolkit = OAuthToolkit()
   toolkit.with_private("private_key.pem")
   toolkit.with_public("public_key.pem")

   # 2. Create a token with claims
   toolkit.claims(
       sub="user123",
       name="Alice",
       email="alice@example.com",
       role="admin"
   )
   token = toolkit.token
   print(f"Created token: {token}")

   # 3. Export JWKS (public key for distribution)
   jwks = toolkit.jwks
   print(f"\nJWKS:\n{jwks}")

   # 4. Validate the token
   claims = toolkit.validate(token)
   print(f"\nValidated claims: {claims}")

Run it:

.. code-block:: bash

   python quickstart.py

Expected output (token will differ):

.. code-block:: none

   Created token: eyJhbGciOiJSUzI1NiIsImtpZCI6IjUxN...

   JWKS:
   {
     "keys": [
       {
         "n": "43CteJFzpZAa_h2...",
         "e": "AQAB",
         "kty": "RSA",
         "alg": "RS256",
         "kid": "5171a100-e4c8-49ed-94af-6bc8fa635368"
       }
     ]
   }

   Validated claims: {'sub': 'user123', 'name': 'Alice', 'email': 'alice@example.com', 'role': 'admin'}

Asynchronous Example
--------------------

Create a file ``async_quickstart.py``:

.. code-block:: python
   :caption: async_quickstart.py

   import asyncio
   from oatk import AsyncOAuthToolkit

   async def main():
       # 1. Configure the toolkit
       toolkit = AsyncOAuthToolkit()
       await toolkit.with_private("private_key.pem")
       await toolkit.with_public("public_key.pem")

       # 2. Create a token
       toolkit.claims(
           sub="user456",
           name="Bob",
           email="bob@example.com"
       )
       token = toolkit.token
       print(f"Created token: {token}")

       # 3. Validate the token
       claims = await toolkit.validate(token)
       print(f"\nValidated claims: {claims}")

   asyncio.run(main())

Run it:

.. code-block:: bash

   pip install oatk[async]  # Ensure async support
   python async_quickstart.py

Using an OAuth Provider
------------------------

Instead of managing keys yourself, you can use an OAuth provider:

.. code-block:: python

   from oatk import OAuthToolkit

   toolkit = OAuthToolkit()
   toolkit.using_provider(
       "https://accounts.google.com/.well-known/openid-configuration"
   )
   toolkit.with_client_id("your-client-id")

   # Now you can validate tokens from Google
   claims = toolkit.validate(token)

For async:

.. code-block:: python

   from oatk import AsyncOAuthToolkit

   async def main():
       toolkit = AsyncOAuthToolkit()
       await toolkit.using_provider(
           "https://accounts.google.com/.well-known/openid-configuration"
       )
       claims = await toolkit.validate(token)

Flask Integration
-----------------

Protect Flask routes with decorators:

.. code-block:: python
   :caption: app.py

   from flask import Flask
   from oatk import OAuthToolkit

   app = Flask(__name__)
   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   @app.route("/public")
   def public():
       return {"message": "public endpoint"}

   @app.route("/protected")
   @toolkit.authenticated
   def protected():
       return {"message": "authenticated user"}

   @app.route("/admin")
   @toolkit.authenticated_with_claims(role="admin")
   def admin():
       return {"message": "admin only"}

   if __name__ == "__main__":
       app.run(debug=True)

Test it:

.. code-block:: bash

   # Get a token (from your OAuth provider or generate one)
   curl http://localhost:5000/protected -H "Authorization: Bearer <token>"
   curl http://localhost:5000/admin -H "Authorization: Bearer <token>"

FastAPI Integration
-------------------

Use dependency injection with FastAPI:

.. code-block:: python
   :caption: main.py

   from fastapi import FastAPI, Depends
   from oatk.async_toolkit import AsyncOAuthToolkit
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

   @app.get("/admin")
   async def admin(user = Depends(oauth.require_claims(role="admin"))):
       return {"message": "admin access"}

Command Line Usage
------------------

oatk provides a CLI for quick operations:

**Generate JWKS from public key:**

.. code-block:: bash

   oatk with_public public_key.pem jwks > certs.json

**Create a token:**

.. code-block:: bash

   oatk with_private private_key.pem \
        with_jwks certs.json \
        claims '{"sub":"user123","role":"admin"}' \
        token > token.txt

**Validate a token:**

.. code-block:: bash

   oatk with_jwks certs.json from_file token.txt validate

**Decode without validation:**

.. code-block:: bash

   oatk from_file token.txt decode

Common Patterns
---------------

**Token Generation Service:**

.. code-block:: python

   from oatk import OAuthToolkit

   def create_token(user_id, role):
       toolkit = OAuthToolkit()
       toolkit.with_private("private_key.pem")
       toolkit.claims(sub=user_id, role=role)
       return toolkit.token

**Token Validation Middleware:**

.. code-block:: python

   from oatk import OAuthToolkit

   toolkit = OAuthToolkit()
   toolkit.using_provider("https://.../.well-known/openid-configuration")

   def validate_request(request):
       auth_header = request.headers.get("Authorization")
       if not auth_header or not auth_header.startswith("Bearer "):
           return None
       token = auth_header[7:]
       try:
           return toolkit.validate(token)
       except Exception:
           return None

**JWT Claims Validation:**

.. code-block:: python

   from oatk import OAuthToolkit

   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   # Validate with specific claims
   claims = toolkit.validate(token)

   # Check claims manually
   if claims.get("role") == "admin":
       # Grant admin access
       pass

   # Or use decorators
   @toolkit.authenticated_with_claims(role="admin")
   def admin_route():
       return "admin only"

Next Steps
----------

Now that you've completed the quickstart:

- Read the :doc:`sync-api` documentation for detailed synchronous usage
- Read the :doc:`async-api` documentation for detailed async usage
- Learn about :doc:`integrations` with web frameworks
- Explore the :doc:`api-reference` for complete API details
- Review the :doc:`security` considerations