Security Considerations
======================

.. warning::

   This software deals with authentication and authorization, which are
   critical security components. All software can contain bugs, including
   security vulnerabilities.

Security Disclaimer
-------------------

By using this software, you acknowledge that:

- You understand the security implications
- You take responsibility for any security-related issues
- This toolkit is designed primarily for prototypes and learning
- For production systems, consider battle-tested alternatives like
  Authlib, python-jose, or similar

**USE AT YOUR OWN RISK.** The authors and contributors are not responsible
for any security breaches, data loss, or other damages resulting from the
use of this software.

Intended Use Cases
------------------

oatk is designed for:

- **Quick prototypes**: Get OAuth up and running quickly
- **Learning**: Understand OAuth/JWT concepts
- **Development environments**: Test OAuth flows without complex setup
- **Understanding**: See what's happening under the hood

For production systems, we recommend:

- **Authlib**: Comprehensive OAuth/JWT library with security best practices
- **python-jose**: Jose ecosystem implementation with security audits
- **PyJWT**: Lower-level JWT library with security features

Key Security Features
--------------------

oatk implements the following security features:

Token Validation
~~~~~~~~~~~~~~~~

**Signature Verification**

All tokens are cryptographically signed with RSA:

.. code-block:: python

   # Tokens are validated against public key
   claims = toolkit.validate(token)

   # Invalid signatures are rejected
   toolkit.validate(invalid_token)  # Raises InvalidTokenError

**Algorithm Verification**

Tokens must use RS256 (RSA + SHA-256):

.. code-block:: python

   # Tokens are checked for correct algorithm
   # Prevents algorithm confusion attacks

**Expiration Checking**

Expired tokens are automatically rejected:

.. code-block:: python

   # Tokens with exp < now are rejected
   claims = toolkit.validate(token)  # Raises ExpiredSignatureError

**Audience Validation**

When client_id is set, audience is validated:

.. code-block:: python

   toolkit.with_client_id("your-client-id")
   claims = toolkit.validate(token)  # Checks aud claim

Key Management
~~~~~~~~~~~~~

**Private Key Security**

Keep private keys secure:

.. code-block:: bash

   # Never commit private keys
   echo "private_key.pem" >> .gitignore

   # Use environment variables or secret management
   export PRIVATE_KEY_PATH="/secure/path/private_key.pem"

**Key Rotation**

Rotate keys periodically:

.. code-block:: python

   # JWKS can contain multiple keys
   {
     "keys": [
       {"kid": "key-2024-01", ...},  # Current key
       {"kid": "key-2023-12", ...}   # Previous key (for validation)
     ]
   }

**Provider Security**

Use HTTPS for provider URLs:

.. code-block:: python

   # Always use HTTPS
   await toolkit.using_provider(
       "https://accounts.google.com/.well-known/openid-configuration"
   )

Known Security Considerations
------------------------------

Token Decoding Without Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Risk:** ``decode()`` does NOT validate the signature.

.. code-block:: python

   # UNSAFE - no signature verification
   claims = toolkit.decode(token)

**Use only for:**

- Debugging and inspection
- Trusted environments
- When you need to see claims before validation

**Never use for:**

- Authentication decisions
- Authorization decisions
- Security-critical operations

.. code-block:: python

   # WRONG - never use decode for auth
   claims = toolkit.decode(token)
   if claims["role"] == "admin":
       grant_admin_access()  # SECURITY RISK!

   # CORRECT - always validate for auth
   claims = toolkit.validate(token)
   if claims["role"] == "admin":
       grant_admin_access()

Flask Decorators and Thread Safety
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask decorators use global ``request`` object:

.. code-block:: python

   @app.route("/protected")
   @toolkit.authenticated
   def protected():
       # Uses Flask's request context
       # Safe in Flask's request/response model
       return {"message": "ok"}

**Considerations:**

- Flask's request context is thread-local
- Safe for standard Flask deployment
- Be careful with async Flask extensions

Async Token Management
~~~~~~~~~~~~~~~~~~~~~~

AsyncOAuthToolkit uses ContextVar for token management:

.. code-block:: python

   # Tokens are stored in async context
   toolkit.set_authorization_token(token)

**Considerations:**

- Each async task has its own context
- Context is not shared between tasks
- Must set token before each operation

.. code-block:: python

   # WRONG - token not set
   @toolkit.authenticated
   async def protected():
       return "ok"

   result = await protected()  # Returns 401

   # CORRECT - set token first
   toolkit.set_authorization_token(token)
   result = await protected()

Clock Skew
~~~~~~~~~

Token validation depends on system clock:

.. code-block:: python

   # Expiration check uses current time
   if claims["exp"] < time.time():
       raise ExpiredSignatureError

**Recommendations:**

- Use NTP to synchronize clocks
- Consider clock skew tolerance
- Use short token lifetimes

Token Replay Attacks
~~~~~~~~~~~~~~~~~~~~

oatk does not implement token blacklisting or replay protection.

**Considerations:**

- Tokens remain valid until expiration
- Compromised tokens can be reused
- No built-in revocation mechanism

**Mitigations:**

.. code-block:: python

   # Use short token lifetimes
   toolkit.claims(
       sub="user123",
       exp=int(time.time()) + 300  # 5 minutes
   )

   # Implement token blacklisting (manual)
   revoked_tokens = set()

   def validate_with_blacklist(token):
       if token in revoked_tokens:
           raise InvalidTokenError("Token revoked")
       return toolkit.validate(token)

Missing Token Validation
~~~~~~~~~~~~~~~~~~~~~~~~

Always validate tokens, never trust decoded claims:

.. code-block:: python

   # WRONG - no validation
   claims = toolkit.decode(token)
   grant_access(claims["user"])

   # CORRECT - validate first
   claims = toolkit.validate(token)
   grant_access(claims["user"])

Claim Injection
~~~~~~~~~~~~~~~

Be careful when accepting claims from users:

.. code-block:: python

   # WRONG - trust user input
   user_claims = request.json
   toolkit.claims(**user_claims)
   token = toolkit.token

   # CORRECT - validate claims
   user_claims = request.json
   if "role" in user_claims:
       # Don't allow role injection
       del user_claims["role"]
   toolkit.claims(**user_claims)

Provider Trust
~~~~~~~~~~~~~~

When using OAuth providers:

.. code-block:: python

   # Trust provider's configuration
   await toolkit.using_provider(url)

**Considerations:**

- Provider must use HTTPS
- Provider's keys are trusted
- Provider's claims are trusted
- Verify provider identity

Security Best Practices
----------------------

Private Key Management
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate strong keys
   openssl genrsa -out private_key.pem 4096

   # Set restrictive permissions
   chmod 600 private_key.pem

   # Never commit to version control
   echo "private_key.pem" >> .gitignore

   # Use environment variables
   export PRIVATE_KEY_PATH="/secure/path/private_key.pem"

Token Lifetime
~~~~~~~~~~~~~~

.. code-block:: python

   import time

   # Use appropriate token lifetimes
   toolkit.claims(
       sub="user123",
       iat=int(time.time()),
       exp=int(time.time()) + 3600  # 1 hour
   )

   # For sensitive operations, use shorter lifetimes
   toolkit.claims(
       sub="user123",
       exp=int(time.time()) + 300  # 5 minutes
   )

Claim Validation
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Always validate required claims
   @toolkit.authenticated_with_claims(
       sub=lambda s: s is not None,  # Subject required
       exp=lambda e: e > time.time(),  # Not expired
       iss=lambda i: i in ["trusted-issuer"]  # Known issuer
   )
   def sensitive_route():
       return "ok"

HTTPS Everywhere
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Always use HTTPS for providers
   await toolkit.using_provider(
       "https://provider.com/.well-known/openid-configuration"
   )

   # Serve your API over HTTPS
   # In production, use reverse proxy with TLS

Monitoring and Logging
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging

   # Log authentication events
   logging.basicConfig(level=logging.INFO)

   try:
       claims = toolkit.validate(token)
       logging.info(f"Authentication success: {claims['sub']}")
   except InvalidTokenError as e:
       logging.warning(f"Authentication failed: {e}")

When to Use Alternatives
-------------------------

Consider using Authlib, python-jose, or similar when:

- Building production systems
- Handling sensitive data
- Need security audits and certifications
- Require advanced features (introspection, revocation, etc.)
- Need battle-tested implementations
- Require compliance with security standards

Security Reporting
------------------

If you discover a security vulnerability, please report it responsibly:

1. Do NOT open a public issue
2. Email security concerns to the maintainer
3. Provide details about the vulnerability
4. Allow time for response and fix

Additional Resources
--------------------

- `OAuth 2.0 Security Best Current Practice <https://tools.ietf.org/html/draft-ietf-oauth-security-topics>`_
- `JWT Best Practices <https://tools.ietf.org/html/rfc8725>`_
- `OWASP JWT Security Cheat Sheet <https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html>`_