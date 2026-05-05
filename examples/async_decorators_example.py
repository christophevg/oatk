"""
Example usage of AsyncOAuthToolkit decorators with ASGI frameworks.

This file demonstrates framework-agnostic async decorators that work with
Quart, FastAPI, and Starlette.
"""

import asyncio
import time

from oatk.async_toolkit import AsyncOAuthToolkit


# Example 1: Framework-agnostic usage with manual token setting
async def example_framework_agnostic():
  """
  Framework-agnostic example where you manually set the authorization token.

  This approach works with any ASGI framework.
  """
  toolkit = AsyncOAuthToolkit()

  # Configure toolkit with provider (async operation)
  # await toolkit.using_provider("https://example.com/.well-known/openid-configuration")

  # For this example, we'll use a local key
  await toolkit.with_private("private_key.pem")
  await toolkit.with_public("public_key.pem")

  # Set up claims and generate a token
  toolkit.claims(
    sub="user123",
    iss="https://example.com",
    aud="my-client-id",
    role="admin",
    exp=int(time.time()) + 3600
  )

  token = toolkit.token

  # Define a protected route
  @toolkit.authenticated
  async def protected_route():
    return {"message": "authenticated", "user": "user123"}

  # Set the authorization token before calling the protected route
  toolkit.set_authorization_token(token)

  # Call the protected route
  result = await protected_route()
  print(f"Result: {result}")

  # Define a route with required claims
  @toolkit.authenticated_with_claims(role="admin")
  async def admin_route():
    return {"message": "admin access granted"}

  toolkit.set_authorization_token(token)
  result = await admin_route()
  print(f"Admin result: {result}")


# Example 2: Quart integration
async def example_quart():
  """
  Example with Quart (async Flask).

  In Quart, you would extract the token from the request context.
  """
  # This is pseudo-code showing how it would work in Quart
  toolkit = AsyncOAuthToolkit()
  await toolkit.with_public("public_key.pem")

  # In your Quart app:
  #
  # from quart import Quart, request
  #
  # app = Quart(__name__)
  #
  # @app.route("/protected")
  # @toolkit.authenticated
  # async def protected():
  #     # Extract token from request
  #     auth_header = request.headers.get("Authorization")
  #     toolkit.set_authorization_token(
  #         toolkit.extract_token_from_header(auth_header)
  #     )
  #     return {"message": "authenticated"}
  #
  # @app.route("/admin")
  # @toolkit.authenticated_with_claims(role="admin")
  # async def admin():
  #     auth_header = request.headers.get("Authorization")
  #     toolkit.set_authorization_token(
  #         toolkit.extract_token_from_header(auth_header)
  #     )
  #     return {"message": "admin only"}

  print("Quart example - see comments in code")


# Example 3: FastAPI integration
async def example_fastapi():
  """
  Example with FastAPI.

  FastAPI uses dependency injection, which can be combined with the toolkit.
  """
  # This is pseudo-code showing how it would work in FastAPI
  toolkit = AsyncOAuthToolkit()
  await toolkit.with_public("public_key.pem")

  # In your FastAPI app:
  #
  # from fastapi import FastAPI, Depends, HTTPException, Request
  # from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
  #
  # app = FastAPI()
  # security = HTTPBearer()
  #
  # async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
  #     toolkit.set_authorization_token(credentials.credentials)
  #     try:
  #         claims = await toolkit.validate(credentials.credentials)
  #         return claims
  #     except Exception:
  #         raise HTTPException(status_code=403, detail="Invalid token")
  #
  # async def require_claims(**required_claims):
  #     async def validator(credentials: HTTPAuthorizationCredentials = Depends(security)):
  #         toolkit.set_authorization_token(credentials.credentials)
  #         claims = await toolkit.validate(credentials.credentials)
  #         for claim, value in required_claims.items():
  #             if claim not in claims:
  #                 raise HTTPException(status_code=403, detail=f"Missing claim: {claim}")
  #             if callable(value):
  #                 if not value(claims[claim]):
  #                     raise HTTPException(status_code=403, detail=f"Invalid claim: {claim}")
  #             elif value != claims[claim]:
  #                 raise HTTPException(status_code=403, detail=f"Invalid claim value: {claim}")
  #         return claims
  #     return validator
  #
  # @app.get("/protected")
  # async def protected(user = Depends(get_current_user)):
  #     return {"message": "authenticated", "user": user["sub"]}
  #
  # @app.get("/admin")
  # async def admin(user = Depends(require_claims(role="admin"))):
  #     return {"message": "admin only", "user": user["sub"]}

  print("FastAPI example - see comments in code")


# Example 4: Starlette integration
async def example_starlette():
  """
  Example with Starlette.

  Starlette is the framework that FastAPI is built on.
  """
  # This is pseudo-code showing how it would work in Starlette
  toolkit = AsyncOAuthToolkit()
  await toolkit.with_public("public_key.pem")

  # In your Starlette app:
  #
  # from starlette.applications import Starlette
  # from starlette.routing import Route
  # from starlette.requests import Request
  # from starlette.responses import JSONResponse
  #
  # async def protected(request: Request):
  #     auth_header = request.headers.get("Authorization")
  #     toolkit.set_authorization_token(
  #         toolkit.extract_token_from_header(auth_header)
  #     )
  #
  #     @toolkit.authenticated
  #     async def handler():
  #         return {"message": "authenticated"}
  #
  #     result = await handler()
  #     return JSONResponse(result)
  #
  # app = Starlette(routes=[
  #     Route("/protected", protected)
  # ])

  print("Starlette example - see comments in code")


# Example 5: Middleware pattern for automatic token extraction
async def example_middleware():
  """
  Example showing a middleware pattern for automatic token extraction.

  This would be framework-specific middleware that sets the token before
  the route handler is called.
  """
  toolkit = AsyncOAuthToolkit()
  await toolkit.with_public("public_key.pem")

  # Pseudo-code for a middleware:
  #
  # async def auth_middleware(request, call_next):
  #     # Extract token from request
  #     auth_header = request.headers.get("Authorization")
  #     token = toolkit.extract_token_from_header(auth_header)
  #
  #     # Set token in context
  #     toolkit.set_authorization_token(token)
  #
  #     # Call the next middleware/handler
  #     response = await call_next(request)
  #
  #     # Clear token from context
  #     toolkit.set_authorization_token(None)
  #
  #     return response
  #
  # Now routes can just use @toolkit.authenticated without manual token setting

  print("Middleware example - see comments in code")


async def main():
  """Run all examples."""
  print("=== Example 1: Framework-agnostic ===")
  await example_framework_agnostic()

  print("\n=== Example 2: Quart ===")
  await example_quart()

  print("\n=== Example 3: FastAPI ===")
  await example_fastapi()

  print("\n=== Example 4: Starlette ===")
  await example_starlette()

  print("\n=== Example 5: Middleware ===")
  await example_middleware()


if __name__ == "__main__":
  asyncio.run(main())