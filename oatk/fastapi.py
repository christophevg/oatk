"""
FastAPI integration for AsyncOAuthToolkit.

This module provides dependency injection helpers for using AsyncOAuthToolkit
with FastAPI applications. It follows FastAPI's dependency injection pattern
using Depends() for authentication.

Example:
    from fastapi import FastAPI, Depends
    from oatk.fastapi import OAuthToolkitDependency
    from oatk.async_toolkit import AsyncOAuthToolkit

    app = FastAPI()
    toolkit = AsyncOAuthToolkit()
    await toolkit.using_provider("https://example.com/.well-known/openid-configuration")

    oauth = OAuthToolkitDependency(toolkit)

    @app.get("/protected")
    async def protected(user = Depends(oauth.get_current_user)):
        return {"user": user}

    @app.get("/admin")
    async def admin(user = Depends(oauth.require_claims(role="admin"))):
        return {"admin": user}
"""

from typing import Any, Callable, Dict, List, Union

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from oatk.async_toolkit import AsyncOAuthToolkit

# Type for claim values in require_claims
ClaimValue = Union[str, List[Any], Callable[[Any], bool]]


class OAuthToolkitDependency:
  """
  FastAPI dependency injection wrapper for AsyncOAuthToolkit.

  This class provides FastAPI-compatible dependencies for OAuth authentication.
  It uses FastAPI's HTTPBearer security scheme and dependency injection pattern.

  Attributes:
      toolkit: The AsyncOAuthToolkit instance to use for token validation
      scheme: The HTTPBearer security scheme for extracting tokens

  Example:
      toolkit = AsyncOAuthToolkit()
      await toolkit.with_public("public_key.pem")

      oauth = OAuthToolkitDependency(toolkit)

      @app.get("/protected")
      async def protected(user = Depends(oauth.get_current_user)):
          return {"user": user["sub"]}
  """

  def __init__(self, toolkit: AsyncOAuthToolkit) -> None:
    """
    Initialize the OAuth dependency wrapper.

    Args:
        toolkit: A configured AsyncOAuthToolkit instance
    """
    self._toolkit = toolkit
    self._scheme = HTTPBearer()

  @property
  def toolkit(self) -> AsyncOAuthToolkit:
    """Get the underlying AsyncOAuthToolkit instance."""
    return self._toolkit

  @property
  def scheme(self) -> HTTPBearer:
    """Get the HTTPBearer security scheme."""
    return self._scheme

  async def get_current_user(
    self,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
  ) -> Dict[str, Any]:
    """
    FastAPI dependency that validates the token and returns the decoded claims.

    This dependency:
    1. Extracts the Bearer token from the Authorization header
    2. Validates the token signature and claims
    3. Returns the decoded claims dictionary

    Args:
        request: FastAPI Request object (for potential future use)
        credentials: HTTP Bearer credentials extracted by FastAPI

    Returns:
        Dictionary containing the validated claims from the token

    Raises:
        HTTPException: 401 if token is missing, 403 if token is invalid

    Example:
        @app.get("/protected")
        async def protected(user = Depends(oauth.get_current_user)):
            return {"user_id": user["sub"], "email": user.get("email")}
    """
    token = credentials.credentials

    try:
      claims = await self._toolkit.validate(token)
      return claims
    except Exception as e:
      raise HTTPException(
        status_code=403,
        detail=f"Invalid token: {str(e)}",
      ) from e

  def require_claims(
    self,
    **required_claims: ClaimValue,
  ) -> Callable[..., Dict[str, Any]]:
    """
    Create a FastAPI dependency that validates specific claims.

    This method returns a dependency function that:
    1. Validates the token signature
    2. Checks that required claims exist and match expected values
    3. Returns the decoded claims if validation passes

    Args:
        **required_claims: Required claims as keyword arguments.
                          Values can be:
                          - str: exact match required
                          - list: token claim must contain the value
                          - callable: custom validation function

    Returns:
        Async dependency function for use with Depends()

    Raises:
        HTTPException: 401 if token is missing,
                      403 if token is invalid or claims don't match

    Example:
        # Require specific role
        @app.get("/admin")
        async def admin(user = Depends(oauth.require_claims(role="admin"))):
            return {"message": "admin access granted"}

        # Use callable for custom validation
        @app.get("/premium")
        async def premium(
            user = Depends(oauth.require_claims(
                tier=lambda t: t in ["gold", "platinum"]
            ))
        ):
            return {"message": "premium access granted"}
    """
    async def dependency(
      request: Request,
      credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ) -> Dict[str, Any]:
      token = credentials.credentials

      try:
        # Validate token and get claims
        claims = await self._toolkit.validate(token)

        # Check required claims
        for claim, value in required_claims.items():
          if claim not in claims:
            raise HTTPException(
              status_code=403,
              detail=f"Missing required claim: {claim}",
            )

          if callable(value):
            if not value(claims[claim]):
              raise HTTPException(
                status_code=403,
                detail=f"Claim '{claim}' failed validation",
              )
          elif isinstance(value, list):
            # Check if any of the required values are in the claim
            # (claim can be a list or a single value)
            claim_value = claims[claim]
            if isinstance(claim_value, list):
              if not any(v in claim_value for v in value):
                raise HTTPException(
                  status_code=403,
                  detail=f"Claim '{claim}' missing required value(s)",
                )
            else:
              if claim_value not in value:
                raise HTTPException(
                  status_code=403,
                  detail=f"Claim '{claim}' missing required value(s)",
                )
          elif value != claims[claim]:
            raise HTTPException(
              status_code=403,
              detail=f"Invalid value for claim '{claim}'",
            )

        return claims

      except HTTPException:
        raise
      except Exception as e:
        raise HTTPException(
          status_code=403,
          detail=f"Invalid token: {str(e)}",
        ) from e

    return dependency


__all__ = [
  "OAuthToolkitDependency",
]