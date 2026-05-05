Framework Integrations
=====================

oatk provides integrations for popular Python web frameworks.

Flask (Synchronous)
-------------------

Flask is a synchronous microframework. oatk provides route decorators
for authentication.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install oatk

Basic Setup
~~~~~~~~~~~

.. code-block:: python

   from flask import Flask
   from oatk import OAuthToolkit

   app = Flask(__name__)

   # Configure toolkit
   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   # Public route
   @app.route("/")
   def index():
       return {"message": "public"}

   # Protected route
   @app.route("/protected")
   @toolkit.authenticated
   def protected():
       return {"message": "authenticated"}

Authentication Decorators
~~~~~~~~~~~~~~~~~~~~~~~~

**@authenticated**

Require any valid token:

.. code-block:: python

   @app.route("/protected")
   @toolkit.authenticated
   def protected():
       return {"message": "authenticated"}

Returns:

- ``401 Unauthorized`` if ``Authorization`` header is missing
- ``403 Forbidden`` if token is invalid
- Calls route handler if token is valid

**@authenticated_with_claims**

Require specific claims:

.. code-block:: python

   # Exact match
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

   # Custom validation
   @app.route("/premium")
   @toolkit.authenticated_with_claims(
       tier=lambda t: t in ["gold", "platinum"]
   )
   def premium():
       return {"message": "premium access"}

Accessing Claims
~~~~~~~~~~~~~~~~

Decode claims in your route:

.. code-block:: python

   from flask import request

   @app.route("/profile")
   @toolkit.authenticated
   def profile():
       # Extract token
       token = request.headers["Authorization"][7:]

       # Decode claims
       claims = toolkit.decode(token)

       return {
           "user_id": claims["sub"],
           "name": claims.get("name"),
           "email": claims.get("email")
       }

Flask-RESTful Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flask import Flask, request
   from flask_restful import Resource, Api
   from oatk import OAuthToolkit

   app = Flask(__name__)
   api = Api(app)
   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   class ProtectedResource(Resource):
       @toolkit.authenticated
       def get(self):
           token = request.headers["Authorization"][7:]
           claims = toolkit.decode(token)
           return {"user": claims["sub"]}

   class AdminResource(Resource):
       @toolkit.authenticated_with_claims(role="admin")
       def get(self):
           return {"message": "admin access"}

   api.add_resource(ProtectedResource, "/protected")
   api.add_resource(AdminResource, "/admin")

Complete Flask Example
~~~~~~~~~~~~~~~~~~~~~~

See ``examples/web.py`` in the repository.

Quart (Asynchronous)
--------------------

Quart is an async Flask-compatible framework. oatk provides async
decorators with automatic token extraction.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install oatk[quart]

Basic Setup
~~~~~~~~~~~

.. code-block:: python

   from quart import Quart
   from oatk import AsyncOAuthToolkit
   from oatk.quart import quart_authenticated

   app = Quart(__name__)
   toolkit = AsyncOAuthToolkit()

   @app.before_serving
   async def setup():
       await toolkit.using_provider(
           "https://accounts.google.com/.well-known/openid-configuration"
       )

   @app.route("/protected")
   @quart_authenticated(toolkit)
   async def protected():
       return {"message": "authenticated"}

Authentication Decorators
~~~~~~~~~~~~~~~~~~~~~~~~

**quart_authenticated**

Require valid token (automatic extraction):

.. code-block:: python

   from oatk.quart import quart_authenticated

   @app.route("/protected")
   @quart_authenticated(toolkit)
   async def protected():
       return {"message": "authenticated"}

The decorator:

1. Extracts token from ``request.headers["Authorization"]``
2. Sets token in context
3. Validates token
4. Returns 401/403 on error
5. Calls route handler on success

**quart_authenticated_with_claims**

Require specific claims:

.. code-block:: python

   from oatk.quart import quart_authenticated_with_claims

   @app.route("/admin")
   @quart_authenticated_with_claims(toolkit, role="admin")
   async def admin():
       return {"message": "admin only"}

   @app.route("/manager")
   @quart_authenticated_with_claims(
       toolkit,
       role="manager",
       department="engineering"
   )
   async def manager():
       return {"message": "engineering manager"}

Accessing Claims
~~~~~~~~~~~~~~~~

.. code-block:: python

   from quart import request

   @app.route("/profile")
   @quart_authenticated(toolkit)
   async def profile():
       token = toolkit.extract_token_from_header(
           request.headers.get("Authorization")
       )
       claims = toolkit.decode(token)
       return {"user": claims["sub"]}

Complete Quart Example
~~~~~~~~~~~~~~~~~~~~~~

See ``examples/quart_example.py`` in the repository.

FastAPI (Asynchronous)
----------------------

FastAPI is a modern async framework. oatk provides dependency injection
for authentication.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install oatk[fastapi]

Basic Setup
~~~~~~~~~~~

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

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

**get_current_user**

Basic authentication dependency:

.. code-block:: python

   from fastapi import Depends
   from oatk.fastapi import OAuthToolkitDependency

   oauth = OAuthToolkitDependency(toolkit)

   @app.get("/protected")
   async def protected(user = Depends(oauth.get_current_user)):
       # user contains decoded claims
       return {
           "user_id": user["sub"],
           "email": user.get("email")
       }

Returns:

- ``403 Forbidden`` if token is invalid
- Decoded claims dictionary if valid

**require_claims**

Create dependencies with claim requirements:

.. code-block:: python

   @app.get("/admin")
   async def admin(user = Depends(oauth.require_claims(role="admin"))):
       return {"message": "admin access"}

   @app.get("/manager")
   async def manager(
       user = Depends(oauth.require_claims(
           role="manager",
           department="engineering"
       ))
   ):
       return {"message": "manager access"}

**Custom validation:**

.. code-block:: python

   @app.get("/premium")
   async def premium(
       user = Depends(oauth.require_claims(
           tier=lambda t: t in ["gold", "platinum"]
       ))
   ):
       return {"message": "premium access"}

Combining Dependencies
~~~~~~~~~~~~~~~~~~~~~~

Create reusable dependencies:

.. code-block:: python

   async def get_current_admin(
       user = Depends(oauth.require_claims(role="admin"))
   ) -> dict:
       """Dependency that requires admin role."""
       user["is_admin"] = True
       return user

   @app.get("/admin-dashboard")
   async def admin_dashboard(admin = Depends(get_current_admin)):
       return {"admin": admin}

Multiple Endpoints
~~~~~~~~~~~~~~~~~~

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

   # Public endpoint
   @app.get("/")
   async def root():
       return {"message": "public"}

   # Protected endpoint
   @app.get("/protected")
   async def protected(user = Depends(oauth.get_current_user)):
       return {"user_id": user["sub"]}

   # Admin endpoint
   @app.get("/admin")
   async def admin(user = Depends(oauth.require_claims(role="admin"))):
       return {"admin": user["sub"]}

   # Premium endpoint
   @app.get("/premium")
   async def premium(
       user = Depends(oauth.require_claims(
           tier=lambda t: t in ["gold", "platinum"]
       ))
   ):
       return {"tier": user.get("tier")}

OpenAPI Documentation
~~~~~~~~~~~~~~~~~~~~~

FastAPI automatically generates OpenAPI documentation:

.. code-block:: python

   from fastapi import FastAPI
   from fastapi.security import HTTPBearer

   app = FastAPI(
       title="My API",
       description="API with OAuth authentication",
       version="1.0.0"
   )

   # Security scheme is automatically added
   # Visit http://localhost:8000/docs for interactive docs

Complete FastAPI Example
~~~~~~~~~~~~~~~~~~~~~~~

See ``examples/fastapi_example.py`` in the repository.

Choosing a Framework
--------------------

**Flask** (Synchronous)

- Traditional synchronous Python web apps
- Existing Flask applications
- Simpler deployment (any WSGI server)
- Good for: Traditional web apps, simple APIs

**Quart** (Asynchronous)

- Async Flask-compatible applications
- Need async features (websockets, long-polling)
- Migrating from Flask to async
- Good for: Real-time apps, async APIs

**FastAPI** (Asynchronous)

- Modern async Python applications
- Automatic OpenAPI documentation
- Type hints and validation
- Good for: Modern APIs, microservices

Migration Between Frameworks
----------------------------

The toolkit API is consistent across frameworks:

**Flask:**

.. code-block:: python

   toolkit = OAuthToolkit()
   toolkit.with_jwks("certs.json")

   @app.route("/protected")
   @toolkit.authenticated
   def protected():
       return {"message": "authenticated"}

**Quart:**

.. code-block:: python

   toolkit = AsyncOAuthToolkit()
   await toolkit.with_jwks("certs.json")

   @app.route("/protected")
   @quart_authenticated(toolkit)
   async def protected():
       return {"message": "authenticated"}

**FastAPI:**

.. code-block:: python

   toolkit = AsyncOAuthToolkit()
   await toolkit.with_jwks("certs.json")
   oauth = OAuthToolkitDependency(toolkit)

   @app.get("/protected")
   async def protected(user = Depends(oauth.get_current_user)):
       return {"message": "authenticated"}