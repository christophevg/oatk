"""
Test suite for Quart integration.

Tests verify:
- @toolkit.authenticated decorator
- @toolkit.authenticated_with_claims decorator
- Token extraction from Quart request context
- Error handling for missing/invalid tokens
- Claims validation
"""

import pytest


class TestQuartAuthenticated:
  """Test authenticated decorator with Quart."""

  @pytest.mark.asyncio
  async def test_quart_authenticated_with_valid_token(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A Quart route decorated with @toolkit.authenticated
    When: Request includes valid Authorization header
    Then: Route function should execute and return response
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    # Create a mock Quart request context
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):

      @toolkit.authenticated
      async def protected_route():
        return {"message": "authenticated"}

      result = await protected_route()

    assert result == {"message": "authenticated"}

  @pytest.mark.asyncio
  async def test_quart_authenticated_missing_header(self, private_key_file, public_key_file):
    """
    Given: A Quart route decorated with @toolkit.authenticated
    When: Request missing Authorization header
    Then: Should return 401 error response
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))

    # Create a mock Quart request context without auth header
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=None)

    with patch("quart.request", mock_request):

      @toolkit.authenticated
      async def protected_route():
        return {"message": "should not reach here"}

      result = await protected_route()

    assert result == ("Missing Authorization", 401)

  @pytest.mark.asyncio
  async def test_quart_authenticated_invalid_token(self, public_key_file):
    """
    Given: A Quart route decorated with @toolkit.authenticated
    When: Request includes invalid token
    Then: Should return 403 error response
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_public(str(public_key_file))

    # Create a mock Quart request context with invalid token
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value="Bearer invalid-token")

    with patch("quart.request", mock_request):

      @toolkit.authenticated
      async def protected_route():
        return {"message": "should not reach here"}

      result = await protected_route()

    assert result[1] == 403

  @pytest.mark.asyncio
  async def test_quart_authenticated_preserves_metadata(self, private_key_file, public_key_file):
    """
    Given: A function decorated with @toolkit.authenticated
    When: Checking function metadata
    Then: Original function name and docstring preserved
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))

    @toolkit.authenticated
    async def my_protected_route():
      """This is a protected route."""
      return {"message": "ok"}

    assert my_protected_route.__name__ == "my_protected_route"
    assert my_protected_route.__doc__ == "This is a protected route."


class TestQuartAuthenticatedWithClaims:
  """Test authenticated_with_claims decorator with Quart."""

  @pytest.mark.asyncio
  async def test_quart_authenticated_with_claims_matching_claims(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A Quart route decorated with @toolkit.authenticated_with_claims
    When: Token has all required claims with matching values
    Then: Route function should execute
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    # Create a mock Quart request context
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):

      @toolkit.authenticated_with_claims(sub=sample_claims["sub"])
      async def protected_route():
        return {"message": "authenticated"}

      result = await protected_route()

    assert result == {"message": "authenticated"}

  @pytest.mark.asyncio
  async def test_quart_authenticated_with_claims_missing_claim(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A Quart route decorated with @toolkit.authenticated_with_claims
    When: Token missing required claim
    Then: Should return 403 error
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    # Create a mock Quart request context
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):

      @toolkit.authenticated_with_claims(missing_claim="value")
      async def protected_route():
        return {"message": "should not reach here"}

      result = await protected_route()

    assert result[1] == 403
    assert "required claim" in result[0]
    assert "is missing" in result[0]

  @pytest.mark.asyncio
  async def test_quart_authenticated_with_claims_wrong_value(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A Quart route decorated with @toolkit.authenticated_with_claims
    When: Token has claim with wrong value
    Then: Should return 403 error
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    # Create a mock Quart request context
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):

      @toolkit.authenticated_with_claims(sub="wrong-user")
      async def protected_route():
        return {"message": "should not reach here"}

      result = await protected_route()

    assert result[1] == 403

  @pytest.mark.asyncio
  async def test_quart_authenticated_with_claims_callable_validator(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A Quart route with callable claim validator
    When: Token claim passes validation
    Then: Route function should execute
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    # Create a mock Quart request context
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):

      @toolkit.authenticated_with_claims(sub=lambda x: x.startswith("test-user"))
      async def protected_route():
        return {"message": "authenticated"}

      result = await protected_route()

    assert result == {"message": "authenticated"}

  @pytest.mark.asyncio
  async def test_quart_authenticated_with_claims_preserves_metadata(
    self, private_key_file, public_key_file
  ):
    """
    Given: A function decorated with @toolkit.authenticated_with_claims
    When: Checking function metadata
    Then: Original function name and docstring preserved
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))

    @toolkit.authenticated_with_claims(role="admin")
    async def admin_route():
      """Admin only route."""
      return {"message": "admin"}

    assert admin_route.__name__ == "admin_route"
    assert admin_route.__doc__ == "Admin only route."

  @pytest.mark.asyncio
  async def test_quart_authenticated_with_claims_multiple_claims(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A Quart route with multiple required claims
    When: Token has all required claims
    Then: Route function should execute
    """
    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    # Create a mock Quart request context
    from unittest.mock import MagicMock, patch

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):

      @toolkit.authenticated_with_claims(sub=sample_claims["sub"], iss=sample_claims["iss"])
      async def protected_route():
        return {"message": "authenticated"}

      result = await protected_route()

    assert result == {"message": "authenticated"}


class TestQuartIntegration:
  """Test integration with actual Quart app."""

  @pytest.mark.asyncio
  async def test_with_quart_test_client(self, private_key_file, public_key_file, sample_claims):
    """
    Given: A Quart app with protected routes
    When: Making requests with test client
    Then: Decorators should work correctly
    """
    pytest.importorskip("quart")

    from quart import Quart, jsonify

    from oatk.async_toolkit import AsyncOAuthToolkit

    # Configure toolkit
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    # Create Quart app
    app = Quart(__name__)

    @app.route("/protected")
    @toolkit.authenticated
    async def protected():
      return jsonify({"message": "authenticated"})

    @app.route("/admin")
    @toolkit.authenticated_with_claims(sub=sample_claims["sub"])
    async def admin():
      return jsonify({"message": "admin access"})

    # Test with Quart test client
    async with app.test_client() as client:
      # Test without auth
      response = await client.get("/protected")
      assert response.status_code == 401

      # Test with valid token
      response = await client.get("/protected", headers={"Authorization": f"Bearer {token}"})
      assert response.status_code == 200
      data = await response.get_json()
      assert data["message"] == "authenticated"

      # Test admin route with matching claim
      response = await client.get("/admin", headers={"Authorization": f"Bearer {token}"})
      assert response.status_code == 200
      data = await response.get_json()
      assert data["message"] == "admin access"

  @pytest.mark.asyncio
  async def test_quart_decorator_chain_order(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A Quart route with multiple decorators
    When: Route is called
    Then: Decorators should execute in correct order
    """
    pytest.importorskip("quart")

    from quart import Quart, jsonify

    from oatk.async_toolkit import AsyncOAuthToolkit

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    app = Quart(__name__)

    # Route decorator should be closest to function
    @app.route("/protected")
    @toolkit.authenticated
    async def protected():
      return jsonify({"message": "ok"})

    async with app.test_client() as client:
      response = await client.get("/protected", headers={"Authorization": f"Bearer {token}"})
      assert response.status_code == 200
