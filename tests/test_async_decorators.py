"""
Test suite for AsyncOAuthToolkit decorators.

Tests verify:
- @authenticated decorator for async routes
- @authenticated_with_claims decorator for async routes
- execute_authenticated method
- Token validation
- Claims validation (exact match, list membership, callable)
- Error handling
"""

import pytest

from oatk.async_toolkit import AsyncOAuthToolkit


class TestCreateErrorResponse:
  """Test error response creation."""

  def test_create_error_response_returns_tuple(self):
    """
    Given: An error message and status code
    When: Calling _create_error_response
    Then: Should return (message, status_code) tuple
    """
    toolkit = AsyncOAuthToolkit()

    result = toolkit._create_error_response("Test error", 401)

    assert result == ("Test error", 401)
    assert isinstance(result, tuple)
    assert len(result) == 2


class TestExecuteAuthenticated:
  """Test execute_authenticated method."""

  @pytest.mark.asyncio
  async def test_execute_authenticated_missing_token_returns_401(self):
    """
    Given: A request without Authorization header
    When: Calling execute_authenticated
    Then: Should return 401 error
    """
    from unittest.mock import MagicMock, patch

    toolkit = AsyncOAuthToolkit()

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=None)

    with patch("quart.request", mock_request):
      result = await toolkit.execute_authenticated(lambda: "success", None)

    assert result == ("Missing Authorization", 401)

  @pytest.mark.asyncio
  async def test_execute_authenticated_invalid_token_returns_403(self, public_key_file):
    """
    Given: A request with invalid token
    When: Calling execute_authenticated
    Then: Should return 403 error
    """
    from unittest.mock import MagicMock, patch

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_public(str(public_key_file))

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value="Bearer invalid-token")

    with patch("quart.request", mock_request):
      result = await toolkit.execute_authenticated(lambda: "success", None)

    assert result[1] == 403

  @pytest.mark.asyncio
  async def test_execute_authenticated_valid_token_executes_function(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A valid token
    When: Calling execute_authenticated
    Then: Should execute the function and return result
    """
    from unittest.mock import MagicMock, patch

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):
      result = await toolkit.execute_authenticated(lambda: "success", None)

    assert result == "success"

  @pytest.mark.asyncio
  async def test_execute_authenticated_with_async_function(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A valid token and an async function
    When: Calling execute_authenticated
    Then: Should execute the async function
    """
    from unittest.mock import MagicMock, patch

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    async def async_func():
      return "async success"

    with patch("quart.request", mock_request):
      result = await toolkit.execute_authenticated(async_func, None)

    assert result == "async success"

  @pytest.mark.asyncio
  async def test_execute_authenticated_with_required_claims_success(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A valid token with required claims
    When: Calling execute_authenticated with required_claims
    Then: Should execute the function
    """
    from unittest.mock import MagicMock, patch

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):
      result = await toolkit.execute_authenticated(lambda: "success", {"sub": sample_claims["sub"]})

    assert result == "success"

  @pytest.mark.asyncio
  async def test_execute_authenticated_with_required_claims_missing_claim(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A valid token missing required claim
    When: Calling execute_authenticated with required_claims
    Then: Should return 403 error
    """
    from unittest.mock import MagicMock, patch

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    mock_request = MagicMock()
    mock_request.headers.get = MagicMock(return_value=f"Bearer {token}")

    with patch("quart.request", mock_request):
      result = await toolkit.execute_authenticated(lambda: "success", {"missing_claim": "value"})

    assert result[1] == 403
    assert "required claim" in result[0]
    assert "is missing" in result[0]


class TestAuthenticatedDecorator:
  """Test @authenticated decorator."""

  @pytest.mark.asyncio
  async def test_authenticated_decorator_preserves_function_metadata(
    self, private_key_file, public_key_file
  ):
    """
    Given: A function decorated with @authenticated
    When: Checking function metadata
    Then: Original function name and docstring preserved
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))

    @toolkit.authenticated
    async def my_protected_route():
      """This is a protected route."""
      return {"message": "ok"}

    assert my_protected_route.__name__ == "my_protected_route"
    assert my_protected_route.__doc__ == "This is a protected route."


class TestAuthenticatedWithClaimsDecorator:
  """Test @authenticated_with_claims decorator."""

  @pytest.mark.asyncio
  async def test_authenticated_with_claims_preserves_metadata(
    self, private_key_file, public_key_file
  ):
    """
    Given: A function decorated with @authenticated_with_claims
    When: Checking function metadata
    Then: Original function name and docstring preserved
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))

    @toolkit.authenticated_with_claims(role="admin")
    async def admin_route():
      """Admin only route."""
      return {"message": "admin"}

    assert admin_route.__name__ == "admin_route"
    assert admin_route.__doc__ == "Admin only route."
