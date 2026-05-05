Command Line Interface
=====================

oatk provides a command-line interface for quick OAuth operations.

Installation
------------

The CLI is automatically installed with oatk:

.. code-block:: bash

   pip install oatk
   oatk --help

Basic Usage
-----------

The CLI uses Python's Fire library, exposing all OAuthToolkit methods:

.. code-block:: bash

   oatk [method] [args...]

All methods return the toolkit object, enabling method chaining.

Generating JWKS
---------------

Export your public key as JWKS:

.. code-block:: bash

   oatk with_public public_key.pem jwks

Output:

.. code-block:: json

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

Save to file:

.. code-block:: bash

   oatk with_public public_key.pem jwks > certs.json

Creating Tokens
---------------

Create a token with custom claims:

.. code-block:: bash

   oatk with_private private_key.pem \
        with_jwks certs.json \
        claims '{"sub":"user123","role":"admin"}' \
        token

Output (token string):

.. code-block:: none

   eyJhbGciOiJSUzI1NiIsImtpZCI6IjUxNzFhMTAwLWU0YzgtNDllZC05NGFmLTZiYzhmYTYzNTM2OCIsInR5cCI6IkpXVCJ9...

Save to file:

.. code-block:: bash

   oatk with_private private_key.pem \
        with_jwks certs.json \
        claims '{"sub":"user123"}' \
        token > token.txt

Validating Tokens
-----------------

Validate a token from a file:

.. code-block:: bash

   oatk with_jwks certs.json from_file token.txt validate

Output (decoded claims):

.. code-block:: none

   sub: user123
   role: admin

Validate a token from clipboard (macOS):

.. code-block:: bash

   # Copy token to clipboard first
   pbcopy < token.txt  # macOS

   oatk with_jwks certs.json from_clipboard validate

Validate with provider:

.. code-block:: bash

   oatk using_provider "https://accounts.google.com/.well-known/openid-configuration" \
        with_client_id "your-client-id" \
        from_file token.txt \
        validate

Decoding Tokens
---------------

Decode a token without validation:

.. code-block:: bash

   oatk from_file token.txt decode

Output:

.. code-block:: none

   sub: user123
   role: admin
   iat: 1234567890
   exp: 1234571490

Method Chaining
---------------

All methods return the toolkit, enabling chaining:

.. code-block:: bash

   # Create and validate in one line
   oatk with_private private_key.pem \
        with_public public_key.pem \
        claims '{"sub":"test"}' \
        token | \
        oatk with_jwks certs.json from_clipboard validate

Common Workflows
----------------

Setup a New Project
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Generate keys
   openssl genrsa -out private_key.pem 2048
   openssl rsa -in private_key.pem -outform PEM -pubout -out public_key.pem

   # 2. Generate JWKS
   oatk with_public public_key.pem jwks > certs.json

   # 3. Create test token
   oatk with_private private_key.pem \
        with_jwks certs.json \
        claims '{"sub":"test-user","role":"admin"}' \
        token > token.txt

   # 4. Validate token
   oatk with_jwks certs.json from_file token.txt validate

Token Inspection
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Decode header
   oatk from_file token.txt header

   # Decode claims
   oatk from_file token.txt decode

   # Full validation
   oatk with_jwks certs.json from_file token.txt validate

Provider Testing
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test Google provider
   oatk using_provider "https://accounts.google.com/.well-known/openid-configuration" \
        with_client_id "your-client-id" \
        from_file google_token.txt \
        validate

Debugging
---------

**Check toolkit version:**

.. code-block:: bash

   oatk version

**Validate with debug output:**

.. code-block:: bash

   # Enable logging
   LOG_LEVEL=DEBUG oatk with_jwks certs.json from_file token.txt validate

**Test key loading:**

.. code-block:: bash

   # Test private key
   oatk with_private private_key.pem claims '{}' token

   # Test public key
   oatk with_public public_key.pem jwks

Fake OAuth Server
-----------------

oatk includes a fake OAuth server for testing:

.. code-block:: bash

   # Start fake server
   oatk with_private private_key.pem with_jwks certs.json server run

Server runs on ``http://localhost:5000`` by default.

Endpoints:

- ``/.well-known/openid-configuration``: Provider configuration
- ``/oauth/certs``: JWKS endpoint
- ``/oauth/authorize``: Authorization endpoint
- ``/oauth/token``: Token endpoint
- ``/oauth/userinfo``: User info endpoint

Script Integration
------------------

Use oatk in shell scripts:

.. code-block:: bash

   #!/bin/bash

   # Create token
   TOKEN=$(oatk with_private private_key.pem \
                 with_jwks certs.json \
                 claims "{\"sub\":\"$1\"}" \
                 token)

   # Use token
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/protected

Error Handling
--------------

The CLI exits with non-zero status on errors:

.. code-block:: bash

   # Invalid token
   oatk with_jwks certs.json from_file invalid.txt validate
   # Exit code: 1

   # Missing file
   oatk with_jwks missing.json validate
   # Exit code: 1

Use in scripts:

.. code-block:: bash

   if oatk with_jwks certs.json from_file token.txt validate; then
       echo "Token is valid"
   else
       echo "Token is invalid"
       exit 1
   fi

Platform Support
-----------------

**Clipboard support:**

- macOS: Full support via AppKit
- Linux: Not supported
- Windows: Not supported

**Workaround for Linux/Windows:**

.. code-block:: bash

   # Use from_file instead
   oatk with_jwks certs.json from_file token.txt validate

   # Or pipe directly
   echo "$TOKEN" | oatk with_jwks certs.json from_clipboard validate