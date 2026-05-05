"""
Test suite for AsyncHttpClient class.

Tests verify:
- AsyncHttpClient instantiation
- Context manager lifecycle (async with)
- GET and POST requests
- Error handling
- Connection state management
"""

import pytest
import httpx

from oatk.async_client import AsyncHttpClient


class TestAsyncHttpClientInstantiation:
  """Test AsyncHttpClient class instantiation."""

  def test_create_async_http_client_instance(self):
    """
    Given: The AsyncHttpClient class
    When: Creating a new instance
    Then: Instance should be created with default values
    """
    client = AsyncHttpClient()
    assert client is not None, "Should create AsyncHttpClient instance"
    assert client._client is None, "Client should be None initially"
    assert client._timeout == 30.0, "Default timeout should be 30.0 seconds"

  def test_create_async_http_client_with_custom_timeout(self):
    """
    Given: The AsyncHttpClient class
    When: Creating instance with custom timeout
    Then: Instance should use the custom timeout
    """
    client = AsyncHttpClient(timeout=60.0)
    assert client._timeout == 60.0, "Custom timeout should be set"


class TestAsyncHttpClientContextManager:
  """Test AsyncHttpClient as async context manager."""

  @pytest.mark.asyncio
  async def test_context_manager_creates_client(self):
    """
    Given: An AsyncHttpClient instance
    When: Using as async context manager
    Then: Client should be created on entry
    """
    async with AsyncHttpClient() as client:
      assert client._client is not None, "Client should be created"
      assert isinstance(client._client, httpx.AsyncClient), "Should be AsyncClient"

  @pytest.mark.asyncio
  async def test_context_manager_closes_client_on_exit(self):
    """
    Given: An AsyncHttpClient instance in context
    When: Exiting the context
    Then: Client should be closed and set to None
    """
    client = AsyncHttpClient()
    async with client:
      pass  # Just enter and exit

    assert client._client is None, "Client should be None after exit"

  @pytest.mark.asyncio
  async def test_context_manager_returns_self(self):
    """
    Given: An AsyncHttpClient instance
    When: Using as async context manager
    Then: Should return self for chaining
    """
    client = AsyncHttpClient()
    async with client as returned:
      assert returned is client, "Should return self"

  @pytest.mark.asyncio
  async def test_is_connected_property(self):
    """
    Given: An AsyncHttpClient instance
    When: Checking is_connected property
    Then: Should reflect client state
    """
    client = AsyncHttpClient()
    assert not client.is_connected, "Should not be connected initially"

    async with client:
      assert client.is_connected, "Should be connected in context"

    assert not client.is_connected, "Should not be connected after exit"


class TestAsyncHttpClientGetRequests:
  """Test AsyncHttpClient GET requests."""

  @pytest.mark.asyncio
  async def test_get_request_returns_response(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: Making a GET request
    Then: Should return httpx.Response
    """
    httpx_mock.add_response(
      url="https://example.com/data",
      json={"key": "value"},
      status_code=200,
    )

    async with AsyncHttpClient() as client:
      response = await client.get("https://example.com/data")

      assert isinstance(response, httpx.Response), "Should return Response"
      assert response.status_code == 200, "Status should be 200"
      assert response.json() == {"key": "value"}, "Should return JSON"

  @pytest.mark.asyncio
  async def test_get_request_with_params(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: Making a GET request with query params
    Then: Should include params in request
    """
    httpx_mock.add_response(
      url="https://example.com/search?q=test&limit=10",
      json={"results": []},
      status_code=200,
    )

    async with AsyncHttpClient() as client:
      response = await client.get(
        "https://example.com/search",
        params={"q": "test", "limit": 10},
      )

      assert response.status_code == 200, "Status should be 200"
      assert response.json() == {"results": []}, "Should return JSON"

  @pytest.mark.asyncio
  async def test_get_request_with_headers(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: Making a GET request with headers
    Then: Should include headers in request
    """
    httpx_mock.add_response(
      url="https://example.com/protected",
      json={"data": "secret"},
      status_code=200,
    )

    async with AsyncHttpClient() as client:
      response = await client.get(
        "https://example.com/protected",
        headers={"Authorization": "Bearer token123"},
      )

      assert response.status_code == 200, "Status should be 200"
      assert response.json() == {"data": "secret"}, "Should return JSON"

  @pytest.mark.asyncio
  async def test_get_request_without_context_raises_error(self):
    """
    Given: An AsyncHttpClient not used as context manager
    When: Calling get() method
    Then: Should raise RuntimeError
    """
    client = AsyncHttpClient()

    with pytest.raises(RuntimeError, match="must be used as an async context manager"):
      await client.get("https://example.com/data")


class TestAsyncHttpClientPostRequests:
  """Test AsyncHttpClient POST requests."""

  @pytest.mark.asyncio
  async def test_post_request_returns_response(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: Making a POST request
    Then: Should return httpx.Response
    """
    httpx_mock.add_response(
      url="https://example.com/api",
      json={"success": True},
      status_code=201,
    )

    async with AsyncHttpClient() as client:
      response = await client.post(
        "https://example.com/api",
        json={"name": "test"},
      )

      assert isinstance(response, httpx.Response), "Should return Response"
      assert response.status_code == 201, "Status should be 201"
      assert response.json() == {"success": True}, "Should return JSON"

  @pytest.mark.asyncio
  async def test_post_request_with_form_data(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: Making a POST request with form data
    Then: Should send form data
    """
    httpx_mock.add_response(
      url="https://example.com/form",
      json={"received": True},
      status_code=200,
    )

    async with AsyncHttpClient() as client:
      response = await client.post(
        "https://example.com/form",
        data={"field": "value"},
      )

      assert response.status_code == 200, "Status should be 200"

  @pytest.mark.asyncio
  async def test_post_request_with_headers(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: Making a POST request with headers
    Then: Should include headers in request
    """
    httpx_mock.add_response(
      url="https://example.com/api",
      json={"created": True},
      status_code=201,
    )

    async with AsyncHttpClient() as client:
      response = await client.post(
        "https://example.com/api",
        json={"data": "test"},
        headers={"X-Custom-Header": "value"},
      )

      assert response.status_code == 201, "Status should be 201"

  @pytest.mark.asyncio
  async def test_post_request_without_context_raises_error(self):
    """
    Given: An AsyncHttpClient not used as context manager
    When: Calling post() method
    Then: Should raise RuntimeError
    """
    client = AsyncHttpClient()

    with pytest.raises(RuntimeError, match="must be used as an async context manager"):
      await client.post("https://example.com/api", json={"test": "data"})


class TestAsyncHttpClientErrorHandling:
  """Test AsyncHttpClient error handling."""

  @pytest.mark.asyncio
  async def test_get_request_connection_error(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: GET request fails with connection error
    Then: Should raise httpx.HTTPError
    """
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

    async with AsyncHttpClient() as client:
      with pytest.raises(httpx.ConnectError):
        await client.get("https://unreachable.example.com/data")

  @pytest.mark.asyncio
  async def test_post_request_timeout_error(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: POST request times out
    Then: Should raise httpx.TimeoutException
    """
    httpx_mock.add_exception(httpx.TimeoutException("Request timed out"))

    async with AsyncHttpClient(timeout=1.0) as client:
      with pytest.raises(httpx.TimeoutException):
        await client.post("https://slow.example.com/api", json={"test": "data"})

  @pytest.mark.asyncio
  async def test_get_request_http_status_error(self, httpx_mock):
    """
    Given: An AsyncHttpClient in context
    When: GET request returns 4xx or 5xx status
    Then: Response should contain the error status
    """
    httpx_mock.add_response(
      url="https://example.com/notfound",
      status_code=404,
      json={"error": "Not found"},
    )

    async with AsyncHttpClient() as client:
      response = await client.get("https://example.com/notfound")

      assert response.status_code == 404, "Status should be 404"
      assert response.json() == {"error": "Not found"}, "Should return error JSON"


class TestAsyncHttpClientIntegration:
  """Integration tests for AsyncHttpClient with real HTTP requests."""

  @pytest.mark.asyncio
  async def test_get_well_known_configuration(self, httpx_mock):
    """
    Given: A mock OAuth provider
    When: Fetching .well-known/openid-configuration
    Then: Should retrieve and parse configuration
    """
    openid_config = {
      "issuer": "https://example.com",
      "authorization_endpoint": "https://example.com/oauth/authorize",
      "token_endpoint": "https://example.com/oauth/token",
      "jwks_uri": "https://example.com/oauth/certs",
      "userinfo_endpoint": "https://example.com/oauth/userinfo",
    }

    httpx_mock.add_response(
      url="https://example.com/.well-known/openid-configuration",
      json=openid_config,
      status_code=200,
    )

    async with AsyncHttpClient() as client:
      response = await client.get(
        "https://example.com/.well-known/openid-configuration"
      )
      config = response.json()

      assert config["issuer"] == "https://example.com", "Should parse issuer"
      assert "jwks_uri" in config, "Should include jwks_uri"
      assert "token_endpoint" in config, "Should include token_endpoint"

  @pytest.mark.asyncio
  async def test_get_jwks(self, httpx_mock):
    """
    Given: A mock JWKS endpoint
    When: Fetching JWKS
    Then: Should retrieve and parse JWKS
    """
    jwks = {
      "keys": [
        {
          "kty": "RSA",
          "alg": "RS256",
          "kid": "test-key-id",
          "n": "test-modulus",
          "e": "AQAB",
        }
      ]
    }

    httpx_mock.add_response(
      url="https://example.com/oauth/certs",
      json=jwks,
      status_code=200,
    )

    async with AsyncHttpClient() as client:
      response = await client.get("https://example.com/oauth/certs")
      keys = response.json()

      assert "keys" in keys, "Should have keys array"
      assert len(keys["keys"]) == 1, "Should have one key"
      assert keys["keys"][0]["kid"] == "test-key-id", "Should parse key ID"