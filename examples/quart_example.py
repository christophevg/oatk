"""
Example usage of oatk with Quart framework.

This example demonstrates:
1. Setting up AsyncOAuthToolkit with a provider
2. Using @toolkit.authenticated decorator
3. Using @toolkit.authenticated_with_claims decorator
4. Token generation for testing

To run this example:
    uv pip install quart
    python examples/quart_example.py
"""

import asyncio
import time

from oatk.async_toolkit import AsyncOAuthToolkit


async def create_test_keys():
  """Create test keys for the example."""
  from cryptography.hazmat.backends import default_backend
  from cryptography.hazmat.primitives import serialization
  from cryptography.hazmat.primitives.asymmetric import rsa

  # Generate RSA key pair
  private_key = rsa.generate_private_key(
    public_exponent=65537, key_size=2048, backend=default_backend()
  )
  public_key = private_key.public_key()

  # Serialize to PEM format
  private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
  )

  public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
  )

  return private_pem, public_pem


def create_quart_app(toolkit: AsyncOAuthToolkit) -> "Quart":  # noqa: F821
  """
  Create a Quart application with protected routes.

  Args:
      toolkit: Configured AsyncOAuthToolkit instance

  Returns:
      Quart application with protected routes
  """
  from quart import Quart, jsonify

  app = Quart(__name__)

  @app.route("/")
  async def index():
    return jsonify({"message": "Welcome to the API"})

  @app.route("/protected")
  @toolkit.authenticated
  async def protected():
    return jsonify({"message": "This is a protected route"})

  @app.route("/admin")
  @toolkit.authenticated_with_claims(role="admin")
  async def admin():
    return jsonify({"message": "Admin access granted"})

  @app.route("/user")
  @toolkit.authenticated_with_claims(sub="test-user-123")
  async def user_route():
    return jsonify({"message": "Specific user access granted"})

  @app.route("/validator")
  @toolkit.authenticated_with_claims(exp=lambda exp: exp > time.time())
  async def validator_route():
    return jsonify({"message": "Token is valid and not expired"})

  return app


async def main():
  """
  Run the Quart example.

  This demonstrates:
  1. Creating and configuring AsyncOAuthToolkit
  2. Creating a Quart app with protected routes
  3. Generating tokens for testing
  4. Testing protected routes with httpx
  """
  # Create test keys
  import tempfile
  from pathlib import Path

  private_pem, public_pem = await create_test_keys()

  # Save keys to temp files
  with tempfile.TemporaryDirectory() as tmpdir:
    private_path = Path(tmpdir) / "private_key.pem"
    public_path = Path(tmpdir) / "public_key.pem"

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)

    # Configure toolkit
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_path))
    await toolkit.with_public(str(public_path))
    toolkit.with_client_id("test-client-id")

    # Generate test tokens
    toolkit.claims(
      sub="test-user-123",
      iss="https://test.example.com",
      aud="test-client-id",
      role="admin",
      exp=int(time.time()) + 3600,
    )
    admin_token = toolkit.token

    toolkit.claims(
      sub="test-user-456",
      iss="https://test.example.com",
      aud="test-client-id",
      role="user",
      exp=int(time.time()) + 3600,
    )
    user_token = toolkit.token

    toolkit.claims(
      sub="test-user-123",
      iss="https://test.example.com",
      aud="test-client-id",
      role="user",
      exp=int(time.time()) + 3600,
    )
    specific_user_token = toolkit.token

    # Create Quart app
    app = create_quart_app(toolkit)

    # Test with httpx async client
    try:
      import httpx  # noqa: F401
    except ImportError:
      print("httpx not installed. Install with: uv pip install httpx")
      print("\nExample code structure:")
      print("  toolkit = AsyncOAuthToolkit()")
      print("  await toolkit.with_private('private_key.pem')")
      print("  await toolkit.with_public('public_key.pem')")
      print()
      print("  @app.route('/protected')")
      print("  @toolkit.authenticated")
      print("  async def protected():")
      print("      return {'message': 'authenticated'}")
      return

    async with app.test_client() as client:
      print("Testing Quart OAuth Integration")
      print("=" * 50)

      # Test public route
      print("\n1. Testing public route (no auth required):")
      response = await client.get("/")
      print(f"   Status: {response.status_code}")
      print(f"   Data: {await response.get_json()}")

      # Test protected route without token
      print("\n2. Testing protected route without token:")
      response = await client.get("/protected")
      print(f"   Status: {response.status_code}")
      print(f"   Data: {await response.get_json()}")

      # Test protected route with valid token
      print("\n3. Testing protected route with valid admin token:")
      response = await client.get(
        "/protected", headers={"Authorization": f"Bearer {admin_token}"}
      )
      print(f"   Status: {response.status_code}")
      print(f"   Data: {await response.get_json()}")

      # Test admin route with admin token
      print("\n4. Testing admin route with admin token:")
      response = await client.get(
        "/admin", headers={"Authorization": f"Bearer {admin_token}"}
      )
      print(f"   Status: {response.status_code}")
      print(f"   Data: {await response.get_json()}")

      # Test admin route with non-admin token
      print("\n5. Testing admin route with non-admin token:")
      response = await client.get(
        "/admin", headers={"Authorization": f"Bearer {user_token}"}
      )
      print(f"   Status: {response.status_code}")
      print(f"   Data: {await response.get_json()}")

      # Test user-specific route
      print("\n6. Testing user-specific route with matching user:")
      response = await client.get(
        "/user", headers={"Authorization": f"Bearer {specific_user_token}"}
      )
      print(f"   Status: {response.status_code}")
      print(f"   Data: {await response.get_json()}")

      # Test validator route
      print("\n7. Testing validator route with valid token:")
      response = await client.get(
        "/validator", headers={"Authorization": f"Bearer {admin_token}"}
      )
      print(f"   Status: {response.status_code}")
      print(f"   Data: {await response.get_json()}")

      print("\n" + "=" * 50)
      print("All tests completed!")


if __name__ == "__main__":
  asyncio.run(main())
