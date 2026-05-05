Examples
========

This section provides complete, working examples for common use cases.

Basic Examples
--------------

Token Creation and Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/create-and-validate.py
   :language: python

Flask Web Application
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/web.py
   :language: python

Async Examples
---------------

Async Decorators
~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/async_decorators_example.py
   :language: python

Quart Application
~~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/quart_example.py
   :language: python

FastAPI Application
~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/fastapi_example.py
   :language: python

Google Integration
------------------

.. note::

   The Google example requires creating OAuth credentials in the
   `Google Cloud Console <https://console.cloud.google.com/apis/dashboard>`_.

Google Example
~~~~~~~~~~~~~~

See the ``examples/google/`` directory in the repository.

Client Application
~~~~~~~~~~~~~~~~~~

See the ``examples/client/`` directory in the repository.

Testing Examples
----------------

Token Generation for Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from oatk import OAuthToolkit

   def create_test_token(claims):
       """Create a test token for unit tests."""
       toolkit = OAuthToolkit()
       toolkit.with_private("test_private_key.pem")

       # Add test claims
       toolkit.claims(**claims)

       return toolkit.token

   # Use in tests
   def test_authenticated_route():
       token = create_test_token({"sub": "test-user", "role": "admin"})
       response = client.get(
           "/protected",
           headers={"Authorization": f"Bearer {token}"}
       )
       assert response.status_code == 200

Token Validation Mock
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from unittest.mock import Mock, patch
   from oatk import OAuthToolkit

   def test_with_mock_validation():
       # Mock the validate method
       toolkit = OAuthToolkit()
       toolkit.validate = Mock(return_value={
           "sub": "test-user",
           "role": "admin"
       })

       # Test your code
       claims = toolkit.validate("any-token")
       assert claims["role"] == "admin"

Integration Testing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from oatk import OAuthToolkit

   @pytest.fixture
   def toolkit():
       """Provide a configured toolkit for tests."""
       toolkit = OAuthToolkit()
       toolkit.with_private("test_private_key.pem")
       toolkit.with_public("test_public_key.pem")
       return toolkit

   def test_protected_endpoint(toolkit, client):
       # Create token
       toolkit.claims(sub="user123", role="user")
       token = toolkit.token

       # Test endpoint
       response = client.get(
           "/protected",
           headers={"Authorization": f"Bearer {token}"}
       )

       assert response.status_code == 200

Common Patterns
---------------

Token Service
~~~~~~~~~~~~~

.. code-block:: python

   from oatk import OAuthToolkit

   class TokenService:
       def __init__(self, private_key_path):
           self.toolkit = OAuthToolkit()
           self.toolkit.with_private(private_key_path)

       def create_token(self, user_id, **extra_claims):
           self.toolkit.claims(
               sub=user_id,
               **extra_claims
           )
           return self.toolkit.token

   # Usage
   service = TokenService("private_key.pem")
   token = service.create_token("user123", role="admin")

Validation Middleware
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from functools import wraps
   from flask import request, jsonify
   from oatk import OAuthToolkit

   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   def require_auth(f):
       @wraps(f)
       def decorated(*args, **kwargs):
           auth_header = request.headers.get("Authorization")
           if not auth_header or not auth_header.startswith("Bearer "):
               return jsonify({"error": "Missing token"}), 401

           token = auth_header[7:]
           try:
               claims = toolkit.validate(token)
           except Exception as e:
               return jsonify({"error": str(e)}), 403

           return f(claims=claims, *args, **kwargs)
       return decorated

   @app.route("/protected")
   @require_auth
   def protected(claims):
       return {"user": claims["sub"]}

Claim-Based Routing
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flask import Flask
   from oatk import OAuthToolkit

   app = Flask(__name__)
   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   @app.route("/api/<path:path>")
   @toolkit.authenticated
   def api_route(path):
       from flask import request
       token = request.headers["Authorization"][7:]
       claims = toolkit.decode(token)

       # Route based on role
       if claims.get("role") == "admin":
           return handle_admin_route(path)
       elif claims.get("role") == "manager":
           return handle_manager_route(path)
       else:
           return handle_user_route(path)

Multi-Tenant Application
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from oatk import OAuthToolkit

   class MultiTenantAuth:
       def __init__(self):
           self.toolkits = {}

       def add_tenant(self, tenant_id, jwks_path):
           toolkit = OAuthToolkit()
           toolkit.with_jwks(jwks_path)
           self.toolkits[tenant_id] = toolkit

       def validate_token(self, tenant_id, token):
           toolkit = self.toolkits.get(tenant_id)
           if not toolkit:
               raise ValueError(f"Unknown tenant: {tenant_id}")
           return toolkit.validate(token)

   # Usage
   auth = MultiTenantAuth()
   auth.add_tenant("tenant1", "tenant1_certs.json")
   auth.add_tenant("tenant2", "tenant2_certs.json")

   claims = auth.validate_token("tenant1", token)

Rate Limiting
~~~~~~~~~~~~~

.. code-block:: python

   from time import time
   from collections import defaultdict
   from flask import Flask, request
   from oatk import OAuthToolkit

   app = Flask(__name__)
   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   # Simple rate limiting
   request_counts = defaultdict(list)

   def check_rate_limit(user_id, max_requests=100, window=3600):
       now = time()
       requests = request_counts[user_id]

       # Remove old requests
       requests[:] = [t for t in requests if now - t < window]

       if len(requests) >= max_requests:
           return False

       requests.append(now)
       return True

   @app.route("/api/resource")
   @toolkit.authenticated
   def resource():
       token = request.headers["Authorization"][7:]
       claims = toolkit.decode(token)
       user_id = claims["sub"]

       if not check_rate_limit(user_id):
           return {"error": "Rate limit exceeded"}, 429

       return {"data": "resource"}

Token Refresh Pattern
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from datetime import datetime, timedelta
   from oatk import OAuthToolkit

   toolkit = OAuthToolkit()
   toolkit.with_private("private_key.pem")

   def create_token_pair(user_id):
       # Access token (short-lived)
       toolkit.claims(
           sub=user_id,
           type="access",
           exp=int((datetime.now() + timedelta(minutes=15)).timestamp())
       )
       access_token = toolkit.token

       # Refresh token (long-lived)
       toolkit.claims(
           sub=user_id,
           type="refresh",
           exp=int((datetime.now() + timedelta(days=7)).timestamp())
       )
       refresh_token = toolkit.token

       return access_token, refresh_token

   def refresh_access_token(refresh_token):
       claims = toolkit.validate(refresh_token)

       if claims.get("type") != "refresh":
           raise ValueError("Invalid token type")

       # Create new access token
       toolkit.claims(
           sub=claims["sub"],
           type="access",
           exp=int((datetime.now() + timedelta(minutes=15)).timestamp())
       )
       return toolkit.token

Performance Tips
-----------------

Cache JWKS
~~~~~~~~~~

.. code-block:: python

   import json
   from oatk import OAuthToolkit

   # Cache JWKS to avoid repeated file reads
   with open("certs.json") as f:
       jwks = json.load(f)

   toolkit = OAuthToolkit()
   toolkit.with_jwks(jwks)  # Use cached JWKS

Reuse Toolkit Instance
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Good - reuse toolkit
   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   for token in tokens:
       claims = toolkit.validate(token)

   # Bad - create new toolkit each time
   for token in tokens:
       toolkit = OAuthToolkit()
       toolkit.with_jwks("certs.json")
       claims = toolkit.validate(token)

Batch Validation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from concurrent.futures import ThreadPoolExecutor
   from oatk import OAuthToolkit

   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   def validate_batch(tokens):
       with ThreadPoolExecutor(max_workers=10) as executor:
           results = executor.map(toolkit.validate, tokens)
       return list(results)