API Reference
=============

This section provides detailed API documentation for all public classes
and methods in oatk.

OAuthToolkit (Sync)
-------------------

.. automodule:: oatk
   :members:
   :undoc-members:
   :show-inheritance:

AsyncOAuthToolkit (Async)
--------------------------

.. automodule:: oatk.async_toolkit
   :members:
   :undoc-members:
   :show-inheritance:

Type Definitions
----------------

.. automodule:: oatk.types
   :members:
   :undoc-members:
   :show-inheritance:

Quart Integration
-----------------

.. automodule:: oatk.quart
   :members:
   :undoc-members:
   :show-inheritance:

FastAPI Integration
-------------------

.. automodule:: oatk.fastapi
   :members:
   :undoc-members:
   :show-inheritance:

CLI Module
----------

.. automodule:: oatk.__main__
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

oatk uses exceptions from the PyJWT library:

.. py:exception:: jwt.InvalidTokenError

   Base exception for all token validation errors.

.. py:exception:: jwt.ExpiredSignatureError

   Token has expired (exp claim is in the past).

.. py:exception:: jwt.InvalidSignatureError

   Token signature is invalid.

.. py:exception:: jwt.DecodeError

   Token cannot be decoded (malformed).

.. py:exception:: jwt.InvalidAudienceError

   Token audience (aud claim) doesn't match client_id.

.. py:exception:: jwt.InvalidIssuerError

   Token issuer (iss claim) is invalid.

Additional exceptions:

.. py:exception:: ValueError

   Raised when required claims are missing or don't match.

.. py:exception:: FileNotFoundError

   Raised when key files cannot be found.

.. py:exception:: RuntimeError

   Raised when clipboard is unavailable (non-macOS).