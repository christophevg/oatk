"""
Example usage of oatk with Quart framework.

This example demonstrates:
1. Setting up AsyncOAuthToolkit with JWKS
2. Using @toolkit.authenticated decorator
3. Using @toolkit.authenticated_with_claims decorator
4. Role-based and user-specific access control

To run this example:
    make quart-example     # Automated test suite
    make quart-server      # Manual server for testing

Or with uvicorn directly:
    uv run uvicorn examples.quart_example:app --reload --port 8000
"""

import time
from pathlib import Path

from quart import Quart, jsonify

from oatk.async_toolkit import AsyncOAuthToolkit

# Create Quart app at module level for ASGI servers
app = Quart(__name__)

# Initialize toolkit
toolkit = AsyncOAuthToolkit()


# Load JWKS when server starts
@app.before_serving
async def setup_toolkit():
  """Configure the OAuth toolkit with JWKS on server startup."""
  script_dir = Path(__file__).parent
  certs_path = script_dir.parent / "certs.json"
  await toolkit.with_jwks(str(certs_path))


# Define routes


@app.route("/")
async def index():
  """Public endpoint that doesn't require authentication."""
  return jsonify({"message": "Welcome to the API"})


@app.route("/protected")
@toolkit.authenticated
async def protected():
  """Protected endpoint that requires a valid token."""
  return jsonify({"message": "This is a protected route"})


@app.route("/admin")
@toolkit.authenticated_with_claims(role="admin")
async def admin():
  """Admin-only endpoint that requires role='admin' claim."""
  return jsonify({"message": "Admin access granted"})


@app.route("/user")
@toolkit.authenticated_with_claims(sub="test-user-123")
async def user_route():
  """User-specific endpoint that requires sub='test-user-123' claim."""
  return jsonify({"message": "Specific user access granted"})


@app.route("/validator")
@toolkit.authenticated_with_claims(exp=lambda exp: exp > time.time())
async def validator_route():
  """Endpoint with custom validation - token must not be expired."""
  return jsonify({"message": "Token is valid and not expired"})
