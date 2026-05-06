"""
Example FastAPI application using AsyncOAuthToolkit with dependency injection.

This example demonstrates:
1. Using OAuthToolkitDependency for authentication
2. Using get_current_user dependency for basic authentication
3. Using require_claims dependency for role-based access control
4. Custom claim validation with callables

To run this example:
    pip install oatk[fastapi] uvicorn
    uvicorn examples.fastapi_example:app --reload

To test:
    # Get a token first (from your OAuth provider or use the token generation below)
    curl -H "Authorization: Bearer <token>" http://localhost:8000/protected
    curl -H "Authorization: Bearer <token>" http://localhost:8000/admin
"""

import time

from fastapi import Depends, FastAPI

from oatk.async_toolkit import AsyncOAuthToolkit
from oatk.fastapi import OAuthToolkitDependency

# Create FastAPI app
app = FastAPI(
  title="OAuth Toolkit FastAPI Example",
  description="Example API with OAuth authentication",
  version="1.0.0",
)

# Initialize the toolkit
# In production, you would use a provider URL:
# toolkit = AsyncOAuthToolkit()
# await toolkit.using_provider("https://accounts.google.com/.well-known/openid-configuration")

# For this example, we'll use local keys
toolkit = AsyncOAuthToolkit()

# Dependency wrapper
oauth = OAuthToolkitDependency(toolkit)


@app.on_event("startup")
async def startup():
  """
  Initialize the OAuth toolkit on startup.

  In production, configure from a provider:
      await toolkit.using_provider("https://your-provider.com/.well-known/openid-configuration")

  Or load keys from files:
      await toolkit.with_public("public_key.pem")
  """
  # For demo purposes, we'll generate a key pair
  # In production, load from files or use provider
  from cryptography.hazmat.backends import default_backend
  from cryptography.hazmat.primitives.asymmetric import rsa

  private_key = rsa.generate_private_key(
    public_exponent=65537, key_size=2048, backend=default_backend()
  )
  public_key = private_key.public_key()

  toolkit._private_key = private_key
  toolkit._public_key = public_key
  toolkit._certs = {toolkit._kid: public_key}
  toolkit.with_client_id("example-client")


# Public endpoint - no authentication required
@app.get("/")
async def root():
  """Public endpoint that doesn't require authentication."""
  return {"message": "Welcome to the OAuth Toolkit FastAPI Example"}


# Protected endpoint - requires valid token
@app.get("/protected")
async def protected(user: dict = Depends(oauth.get_current_user)):
  """
  Protected endpoint that requires a valid token.

  The user parameter will contain the decoded claims from the token.
  """
  return {
    "message": "You are authenticated",
    "user_id": user.get("sub"),
    "email": user.get("email"),
  }


# Admin endpoint - requires admin role
@app.get("/admin")
async def admin(user: dict = Depends(oauth.require_claims(role="admin"))):
  """
  Admin-only endpoint that requires role='admin' claim.

  Returns 403 if the token doesn't have role='admin'.
  """
  return {
    "message": "Admin access granted",
    "user_id": user.get("sub"),
  }


# Premium endpoint - requires premium tier
@app.get("/premium")
async def premium(
  user: dict = Depends(oauth.require_claims(tier=lambda t: t in ["gold", "platinum"])),
):
  """
  Premium endpoint with callable validation.

  The tier claim must be either 'gold' or 'platinum'.
  """
  return {
    "message": "Premium access granted",
    "tier": user.get("tier"),
  }


# Multiple claims requirement
@app.get("/manager")
async def manager(
  user: dict = Depends(
    oauth.require_claims(
      role="manager",
      department="engineering",
    )
  ),
):
  """
  Endpoint requiring multiple claims to match.

  Both role='manager' AND department='engineering' must be present.
  """
  return {
    "message": "Manager access granted",
    "user": user,
  }


# Helper endpoint to generate a test token
@app.get("/generate-token")
async def generate_token(
  sub: str = "test-user",
  role: str = "user",
  email: str = "user@example.com",
  tier: str = "silver",
  department: str = "general",
):
  """
  Generate a test token for testing purposes.

  WARNING: In production, never expose token generation like this!
  This is only for demonstration and testing.
  """
  toolkit.claims(
    sub=sub,
    role=role,
    email=email,
    tier=tier,
    department=department,
    iss="https://example.com",
    aud="example-client",
    iat=int(time.time()),
    exp=int(time.time()) + 3600,  # 1 hour
  )

  token = toolkit.token
  return {
    "token": token,
    "claims": {
      "sub": sub,
      "role": role,
      "email": email,
      "tier": tier,
      "department": department,
    },
    "usage": f"curl -H 'Authorization: Bearer {token}' http://localhost:8000/protected",
  }


# Custom dependency combining authentication with business logic
async def get_current_admin(
  user: dict = Depends(oauth.require_claims(role="admin")),
) -> dict:
  """
  Example of combining dependencies.

  This dependency requires admin role and can be reused across endpoints.
  """
  # Add business logic here (e.g., load user from database)
  user["is_admin"] = True
  return user


@app.get("/admin-dashboard")
async def admin_dashboard(admin: dict = Depends(get_current_admin)):
  """
  Endpoint using a composed dependency.

  The get_current_admin dependency combines authentication with admin check.
  """
  return {
    "message": "Welcome to admin dashboard",
    "admin": admin,
  }


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=8000)
