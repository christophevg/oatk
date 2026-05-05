"""
Quart integration for AsyncOAuthToolkit.

This module provides Quart-specific decorators that automatically extract
the authorization token from the Quart request context, making it easier
to protect async routes.

Quart is an async Flask-compatible framework, so it uses similar decorator
patterns but with async support.
"""

from functools import wraps
from typing import Any, Callable, Union

from oatk.async_toolkit import AsyncOAuthToolkit
from oatk.types import RequiredClaims


def quart_authenticated(toolkit: AsyncOAuthToolkit) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
  """
  Decorator for authenticating Quart async routes.

  This decorator automatically extracts the authorization token from the
  Quart request context before validating it. It wraps the framework-agnostic
  @authenticated decorator with automatic token extraction.

  Args:
      toolkit: An AsyncOAuthToolkit instance configured with keys/provider

  Returns:
      A decorator function that validates authentication before executing
      the decorated route handler.

  Example:
      from quart import Quart
      from oatk.quart import quart_authenticated
      from oatk.async_toolkit import AsyncOAuthToolkit

      app = Quart(__name__)
      toolkit = AsyncOAuthToolkit()
      await toolkit.using_provider("https://...")

      @app.route("/protected")
      @quart_authenticated(toolkit)
      async def protected():
          return {"message": "authenticated"}

  Note:
      This decorator extracts the token from request.headers["Authorization"]
      and sets it in the toolkit context before validation. The token must
      be in the format "Bearer <token>".
  """
  def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Import quart here to avoid hard dependency
      from quart import request

      # Extract token from request
      auth_header = request.headers.get("Authorization")
      token = toolkit.extract_token_from_header(auth_header)

      # Set token in context
      toolkit.set_authorization_token(token)

      # Use the toolkit's execute_authenticated method
      return await toolkit.execute_authenticated(f, None, *args, **kwargs)

    return wrapper

  return decorator


def quart_authenticated_with_claims(
  toolkit: AsyncOAuthToolkit,
  **required_claims: Union[str, Callable[[Any], bool]]
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
  """
  Decorator factory for authenticating Quart async routes with required claims.

  This decorator automatically extracts the authorization token from the
  Quart request context and validates that the token contains the required
  claims with matching values.

  Args:
      toolkit: An AsyncOAuthToolkit instance configured with keys/provider
      **required_claims: Required claims as keyword arguments.
                        Values can be:
                        - str: exact match required
                        - list: token claim must contain all values
                        - callable: custom validation function

  Returns:
      A decorator function that validates authentication and claims before
      executing the decorated route handler.

  Example:
      from quart import Quart
      from oatk.quart import quart_authenticated_with_claims
      from oatk.async_toolkit import AsyncOAuthToolkit

      app = Quart(__name__)
      toolkit = AsyncOAuthToolkit()
      await toolkit.using_provider("https://...")

      @app.route("/admin")
      @quart_authenticated_with_claims(toolkit, role="admin")
      async def admin_panel():
          return {"message": "admin access granted"}

      # With callable validator
      @app.route("/expensive-operation")
      @quart_authenticated_with_claims(
          toolkit,
          exp=lambda exp: exp > time.time()  # Token not expired
      )
      async def expensive_operation():
          return {"message": "operation allowed"}

  Note:
      This decorator extracts the token from request.headers["Authorization"]
      and sets it in the toolkit context before validation.
  """
  def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Import quart here to avoid hard dependency
      from quart import request

      # Extract token from request
      auth_header = request.headers.get("Authorization")
      token = toolkit.extract_token_from_header(auth_header)

      # Set token in context
      toolkit.set_authorization_token(token)

      # Use the toolkit's execute_authenticated method with claims
      return await toolkit.execute_authenticated(f, required_claims, *args, **kwargs)

    return wrapper

  return decorator


__all__ = [
  "quart_authenticated",
  "quart_authenticated_with_claims",
]