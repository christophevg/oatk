Synchronous API (OAuthToolkit)
===============================

The ``OAuthToolkit`` class provides synchronous OAuth/JWT operations for
traditional Python applications and Flask integration.

.. _oauth-toolkit-class:

OAuthToolkit Class
------------------

.. autoclass:: oatk.OAuthToolkit
   :members:
   :show-inheritance:
   :member-order: bysource

Configuration Methods
---------------------

Loading Keys
~~~~~~~~~~~~

**Load Private Key**

.. code-block:: python

   from oatk import OAuthToolkit

   toolkit = OAuthToolkit()
   toolkit.with_private("private_key.pem")

The private key is used to sign tokens.

**Load Public Key**

.. code-block:: python

   toolkit.with_public("public_key.pem")

The public key is used to validate tokens.

**Load JWKS**

Load JSON Web Key Set from file, string, or dictionary:

.. code-block:: python

   # From file
   toolkit.with_jwks("certs.json")

   # From JSON string
   jwks_string = '{"keys": [...]}'
   toolkit.with_jwks(jwks_string)

   # From dictionary
   jwks_dict = {"keys": [...]}
   toolkit.with_jwks(jwks_dict)

Provider Configuration
~~~~~~~~~~~~~~~~~~~~~~

Configure from an OAuth provider's OpenID Connect discovery endpoint:

.. code-block:: python

   toolkit.using_provider(
       "https://accounts.google.com/.well-known/openid-configuration"
   )
   toolkit.with_client_id("your-client-id")

This fetches the provider's configuration and JWKS automatically.

Token Operations
----------------

Creating Tokens
~~~~~~~~~~~~~~

Create signed JWT tokens with custom claims:

.. code-block:: python

   toolkit.with_private("private_key.pem")

   # Set claims
   toolkit.claims(
       sub="user123",
       name="Alice",
       email="alice@example.com",
       role="admin",
       iat=1234567890,  # Issued at
       exp=1234571490   # Expiration
   )

   # Generate token
   token = toolkit.token
   print(token)

**Chain method calls:**

.. code-block:: python

   token = (OAuthToolkit()
       .with_private("private_key.pem")
       .claims(sub="user123", role="admin")
       .token)

Validating Tokens
~~~~~~~~~~~~~~~~~~

Validate token signature and claims:

.. code-block:: python

   toolkit.with_public("public_key.pem")
   claims = toolkit.validate(token)

   # Or with JWKS
   toolkit.with_jwks("certs.json")
   claims = toolkit.validate(token)

**With provider:**

.. code-block:: python

   toolkit.using_provider("https://.../.well-known/openid-configuration")
   toolkit.with_client_id("your-client-id")
   claims = toolkit.validate(token)  # Validates audience

The validation checks:

1. Token signature (using public key or JWKS)
2. Token hasn't expired (exp claim)
3. Audience matches (if client_id is set)

**Handling validation errors:**

.. code-block:: python

   from jwt import InvalidTokenError

   try:
       claims = toolkit.validate(token)
   except InvalidTokenError as e:
       print(f"Invalid token: {e}")

Decoding Tokens
~~~~~~~~~~~~~~~

Decode a token without validating the signature:

.. code-block:: python

   claims = toolkit.decode(token)

**Warning:** This does NOT validate the signature! Only use for debugging
or when you need to inspect claims without validation.

Token Loading
~~~~~~~~~~~~~

**Load from file:**

.. code-block:: python

   toolkit.from_file("token.txt")
   claims = toolkit.validate()

**Load from clipboard (macOS):**

.. code-block:: python

   toolkit.from_clipboard()
   claims = toolkit.validate()

**Manual token:**

.. code-block:: python

   claims = toolkit.validate(token_string)

JWKS Export
-----------

Export your public key as JWKS for distribution:

.. code-block:: python

   toolkit.with_public("public_key.pem")
   jwks = toolkit.jwks

   # Save to file
   with open("certs.json", "w") as f:
       f.write(jwks)

Flask Integration
-----------------

The toolkit provides decorators for protecting Flask routes.

Basic Authentication
~~~~~~~~~~~~~~~~~~~~~

Require any valid token:

.. code-block:: python

   from flask import Flask
   from oatk import OAuthToolkit

   app = Flask(__name__)
   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   @app.route("/protected")
   @toolkit.authenticated
   def protected():
       return {"message": "authenticated"}

   @app.route("/public")
   def public():
       return {"message": "public"}

**How it works:**

1. Extracts ``Authorization: Bearer <token>`` header
2. Validates the token
3. Returns 401 if missing, 403 if invalid
4. Calls the route handler if valid

Claims-Based Authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~

Require specific claims:

.. code-block:: python

   @app.route("/admin")
   @toolkit.authenticated_with_claims(role="admin")
   def admin():
       return {"message": "admin only"}

   # Multiple claims
   @app.route("/manager")
   @toolkit.authenticated_with_claims(
       role="manager",
       department="engineering"
   )
   def manager():
       return {"message": "engineering manager"}

**Claim value types:**

.. code-block:: python

   # Exact match
   @toolkit.authenticated_with_claims(role="admin")

   # List membership
   @toolkit.authenticated_with_claims(permission=["read", "write"])

   # Custom validation function
   @toolkit.authenticated_with_claims(
       exp=lambda exp: exp > time.time()  # Not expired
   )

Accessing Claims in Routes
~~~~~~~~~~~~~~~~~~~~~~~~~~

Decode claims in your route:

.. code-block:: python

   from flask import request

   @app.route("/profile")
   @toolkit.authenticated
   def profile():
       token = request.headers["Authorization"][7:]
       claims = toolkit.decode(token)
       return {"user": claims["sub"], "name": claims.get("name")}

**Using Flask-RESTful:**

.. code-block:: python

   from flask_restful import Resource

   class Profile(Resource):
       @toolkit.authenticated
       def get(self):
           token = request.headers["Authorization"][7:]
           claims = toolkit.decode(token)
           return {"user": claims["sub"]}

CLI Usage
---------

The command line interface exposes all toolkit methods.

**Generate JWKS:**

.. code-block:: bash

   oatk with_public public_key.pem jwks > certs.json

**Create token:**

.. code-block:: bash

   oatk with_private private_key.pem \
        with_jwks certs.json \
        claims '{"sub":"user123","role":"admin"}' \
        token

**Validate token from file:**

.. code-block:: bash

   oatk with_jwks certs.json from_file token.txt validate

**Validate token from clipboard:**

.. code-block:: bash

   # Copy token to clipboard first
   oatk with_jwks certs.json from_clipboard validate

**Decode token:**

.. code-block:: bash

   oatk from_file token.txt decode

**Provider configuration:**

.. code-block:: bash

   oatk using_provider "https://.../.well-known/openid-configuration" \
        with_client_id "your-client-id" \
        from_file token.txt \
        validate

Chaining Methods
-----------------

All configuration methods return ``self`` for method chaining:

.. code-block:: python

   # One-liner validation
   claims = (OAuthToolkit()
       .with_jwks("certs.json")
       .from_file("token.txt")
       .validate())

   # One-liner token creation
   token = (OAuthToolkit()
       .with_private("private_key.pem")
       .claims(sub="user123", role="admin")
       .token)

Error Handling
--------------

Common exceptions:

.. code-block:: python

   from jwt import InvalidTokenError, ExpiredSignatureError
   from cryptography.hazmat.primitives import serialization

   try:
       claims = toolkit.validate(token)
   except ExpiredSignatureError:
       print("Token has expired")
   except InvalidTokenError as e:
       print(f"Invalid token: {e}")
   except FileNotFoundError as e:
       print(f"Key file not found: {e}")

Complete Example
---------------

.. code-block:: python
   :caption: complete_example.py

   from flask import Flask, request, Response
   from flask_restful import Resource, Api
   from oatk import OAuthToolkit

   app = Flask(__name__)
   api = Api(app)

   # Configure toolkit
   toolkit = OAuthToolkit()
   toolkit.with_private("private_key.pem")
   toolkit.with_jwks("certs.json")

   # Public endpoint
   @app.route("/")
   def index():
       return {"message": "Welcome to the API"}

   # Protected endpoint
   @app.route("/protected")
   @toolkit.authenticated
   def protected():
       return {"message": "You are authenticated"}

   # Admin-only endpoint
   @app.route("/admin")
   @toolkit.authenticated_with_claims(role="admin")
   def admin():
       return {"message": "Admin access granted"}

   # Token generation endpoint
   class Token(Resource):
       def get(self):
           claims = {}
           for key, value in request.args.items():
               claims[key] = value
           token = toolkit.claims(**claims).token
           return Response(response=token, status=200, mimetype="text/plain")

   api.add_resource(Token, "/token")

   if __name__ == "__main__":
       app.run(debug=True)

Testing:

.. code-block:: bash

   # Start server
   python complete_example.py

   # Get a token
   curl "http://localhost:5000/token?sub=user123&role=admin"

   # Access protected endpoint
   curl -H "Authorization: Bearer <token>" http://localhost:5000/protected

   # Access admin endpoint
   curl -H "Authorization: Bearer <token>" http://localhost:5000/admin

Next Steps
----------

- Learn about :doc:`async-api` for async operations
- See :doc:`integrations` for Quart and FastAPI
- Read the :doc:`api-reference` for complete API details