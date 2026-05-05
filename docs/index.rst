oatk - OAuth Toolkit Documentation
=================================

A clean, simple Python OAuth toolkit for quick prototypes and learning.
Provides both synchronous and asynchronous implementations with framework
integrations for Flask, Quart, and FastAPI.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   sync-api
   async-api
   integrations
   api-reference

.. toctree::
   :maxdepth: 2
   :caption: Additional Information

   security
   cli
   examples

Features
--------

**Core Features**

- Token creation with RSA private keys
- Token validation with RSA public keys
- JWKS import/export for key distribution
- Provider-based configuration (OpenID Connect)
- Token decoding (without validation)

**Synchronous API (OAuthToolkit)**

- Flask route decorators for authentication
- Command-line interface for quick operations
- Clipboard support (macOS)
- Provider-based initialization

**Asynchronous API (AsyncOAuthToolkit)**

- Async HTTP operations with httpx
- Async file I/O with anyio
- Framework-agnostic decorators
- Context-based token management

**Framework Integrations**

- **Flask** (sync): Route decorators with ``@authenticated`` and ``@authenticated_with_claims``
- **Quart** (async): Automatic token extraction from requests
- **FastAPI** (async): Dependency injection pattern

Use Cases
---------

oatk is designed for:

- **Quick prototypes**: Get OAuth up and running in minutes
- **Learning**: Understand OAuth/JWT concepts with clean, readable code
- **Development environments**: Test OAuth flows without complex setup
- **Understanding**: See what's happening under the hood

For production systems, consider battle-tested alternatives like Authlib,
python-jose, or similar.

Installation
------------

.. code-block:: bash

   pip install oatk

For async support and framework integrations:

.. code-block:: bash

   pip install oatk[async]      # Async support
   pip install oatk[quart]      # Quart integration
   pip install oatk[fastapi]    # FastAPI integration

Quick Example
-------------

**Synchronous:**

.. code-block:: python

   from oatk import OAuthToolkit

   toolkit = OAuthToolkit()
   toolkit.with_private("private_key.pem")

   # Create token
   toolkit.claims(user="alice", role="admin")
   token = toolkit.token

   # Validate token
   claims = toolkit.validate(token)

**Asynchronous:**

.. code-block:: python

   from oatk import AsyncOAuthToolkit

   toolkit = AsyncOAuthToolkit()
   await toolkit.using_provider(
       "https://accounts.google.com/.well-known/openid-configuration"
   )
   claims = await toolkit.validate(token)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`