Installation
============

Requirements
------------

oatk requires:

- Python 3.9 or higher
- RSA key pair (for token signing/validation)

Generating RSA Keys
~~~~~~~~~~~~~~~~~~~

Before using oatk, you need an RSA key pair:

.. code-block:: bash

   # Generate a private key
   openssl genrsa -out private_key.pem 2048

   # Extract the public key
   openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem

**Important:** Keep your private key secure! Never commit it to version control.

Basic Installation
------------------

Install oatk using pip:

.. code-block:: bash

   pip install oatk

This installs the core package with synchronous support and Flask integration.

Installation with Extras
------------------------

oatk provides optional extras for different use cases:

**Async Support**

For async operations with httpx and anyio:

.. code-block:: bash

   pip install oatk[async]

This adds:

- ``httpx``: Modern async HTTP client
- ``anyio``: Async compatibility layer

**Quart Integration**

For Quart (async Flask) applications:

.. code-block:: bash

   pip install oatk[quart]

This adds:

- ``quart``: Async Flask-compatible framework
- ``httpx`` and ``anyio`` for async support

**FastAPI Integration**

For FastAPI applications:

.. code-block:: bash

   pip install oatk[fastapi]

This adds:

- ``fastapi``: Modern async web framework
- ``httpx`` and ``anyio`` for async support

**Development Dependencies**

For development and testing:

.. code-block:: bash

   pip install oatk[dev]

This adds:

- ``pytest``: Testing framework
- ``pytest-asyncio``: Async test support
- ``pytest-httpx``: HTTP mocking for tests
- ``ruff``: Fast Python linter
- ``mypy``: Static type checker
- ``coverage``: Code coverage

Installing Multiple Extras
---------------------------

You can install multiple extras together:

.. code-block:: bash

   pip install oatk[async,fastapi,dev]

From Source
-----------

To install from source for development:

.. code-block:: bash

   git clone https://github.com/christophevg/oatk.git
   cd oatk
   pip install -e .[dev]

Verifying Installation
----------------------

Verify your installation:

.. code-block:: python

   from oatk import OAuthToolkit, AsyncOAuthToolkit

   # Sync version
   toolkit = OAuthToolkit()
   print(f"oatk version: {toolkit.version}")

   # Async version (requires oatk[async])
   try:
       async_toolkit = AsyncOAuthToolkit()
       print("Async support available")
   except ImportError:
       print("Install oatk[async] for async support")

Command Line Interface
----------------------

The command line tool is automatically installed:

.. code-block:: bash

   oatk --help

Dependencies
------------

Core dependencies (always installed):

- ``pyjwt``: JWT encoding and decoding
- ``cryptography``: RSA key handling
- ``authlib``: JWKS support
- ``requests``: HTTP client (sync)
- ``fire``: CLI framework
- ``python-dotenv``: Environment variable loading
- ``flask``: Web framework
- ``flask-cors``: CORS support
- ``flask-restful``: REST API framework
- ``pymongo``: MongoDB driver

Optional dependencies by extra:

- **async**: ``httpx``, ``anyio``
- **quart**: ``quart``, ``httpx``, ``anyio``
- **fastapi**: ``fastapi``, ``httpx``, ``anyio``
- **dev**: ``pytest``, ``pytest-asyncio``, ``pytest-httpx``, ``ruff``, ``mypy``, ``coverage``
- **run**: ``gunicorn``, ``eventlet``

Next Steps
----------

After installation:

1. Generate an RSA key pair (see above)
2. Read the :doc:`quickstart` guide
3. Choose between :doc:`sync-api` or :doc:`async-api`
4. Integrate with your :doc:`integrations`