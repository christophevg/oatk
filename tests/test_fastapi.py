"""
Test suite for FastAPI integration.

Tests verify:
- OAuthToolkitDependency initialization
- get_current_user dependency
- require_claims dependency
- Token extraction from HTTPBearer
- Claims validation (exact match, list membership, callable)
- Error handling (401, 403)
"""

import asyncio
import time

import pytest
from fastapi import Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from oatk.async_toolkit import AsyncOAuthToolkit
from oatk.fastapi import OAuthToolkitDependency


@pytest.fixture
def async_toolkit(private_key_file, public_key_file, sample_claims):
  """
  Create and configure an AsyncOAuthToolkit for testing.

  Uses asyncio to run async initialization synchronously in fixture.

  Args:
      private_key_file: Fixture providing private key file
      public_key_file: Fixture providing public key file
      sample_claims: Fixture providing sample claims

  Returns:
      AsyncOAuthToolkit: Configured toolkit instance
  """
  toolkit = AsyncOAuthToolkit()
  loop = asyncio.get_event_loop()
  loop.run_until_complete(toolkit.with_private(str(private_key_file)))
  loop.run_until_complete(toolkit.with_public(str(public_key_file)))
  toolkit.claims(**sample_claims)
  toolkit.with_client_id(sample_claims.get("aud"))
  return toolkit


@pytest.fixture
def oauth_dependency(async_toolkit):
  """
  Create an OAuthToolkitDependency instance.

  Args:
      async_toolkit: Fixture providing configured toolkit

  Returns:
      OAuthToolkitDependency: Dependency wrapper
  """
  return OAuthToolkitDependency(async_toolkit)


@pytest.fixture
def sample_claims_with_extras(sample_claims):
  """
  Extend sample claims with additional fields for testing.

  Args:
      sample_claims: Base sample claims fixture

  Returns:
      dict: Extended claims dictionary
  """
  claims = sample_claims.copy()
  claims["role"] = "admin"
  claims["tier"] = "gold"
  claims["roles"] = ["admin", "user", "guest"]
  return claims


class TestOAuthToolkitDependencyInit:
  """Test OAuthToolkitDependency initialization."""

  def test_init_with_toolkit(self, async_toolkit):
    """
    Given: An AsyncOAuthToolkit instance
    When: Creating OAuthToolkitDependency
    Then: Should store the toolkit
    """
    dependency = OAuthToolkitDependency(async_toolkit)

    assert dependency.toolkit is async_toolkit

  def test_scheme_property_returns_httpbearer(self, async_toolkit):
    """
    Given: An OAuthToolkitDependency instance
    When: Accessing scheme property
    Then: Should return HTTPBearer instance
    """
    from fastapi.security import HTTPBearer

    dependency = OAuthToolkitDependency(async_toolkit)

    assert isinstance(dependency.scheme, HTTPBearer)


class TestGetCurrentUser:
  """Test get_current_user dependency."""

  @pytest.mark.asyncio
  async def test_get_current_user_valid_token(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A valid JWT token
    When: Calling get_current_user dependency
    Then: Should return decoded claims
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)

    # Create mock credentials
    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = token

    # Create mock request
    from unittest.mock import MagicMock

    request = MagicMock()

    result = await oauth.get_current_user(request, credentials)

    assert result["sub"] == sample_claims["sub"]
    assert result["aud"] == sample_claims["aud"]

  @pytest.mark.asyncio
  async def test_get_current_user_invalid_token_raises_403(
    self,
    public_key_file,
  ):
    """
    Given: An invalid JWT token
    When: Calling get_current_user dependency
    Then: Should raise HTTPException with 403 status
    """
    from fastapi import HTTPException

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_public(str(public_key_file))

    oauth = OAuthToolkitDependency(toolkit)

    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = "invalid-token"

    request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
      await oauth.get_current_user(request, credentials)

    assert exc_info.value.status_code == 403
    assert "Invalid token" in exc_info.value.detail


class TestRequireClaims:
  """Test require_claims dependency factory."""

  @pytest.mark.asyncio
  async def test_require_claims_exact_match(
    self, private_key_file, public_key_file, sample_claims_with_extras
  ):
    """
    Given: A valid token with required claim
    When: Calling require_claims dependency
    Then: Should return claims when claim matches
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims_with_extras)
    toolkit.with_client_id(sample_claims_with_extras.get("aud"))

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)
    dependency = oauth.require_claims(role="admin")

    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = token

    request = MagicMock()

    result = await dependency(request, credentials)

    assert result["role"] == "admin"

  @pytest.mark.asyncio
  async def test_require_claims_missing_claim_raises_403(
    self, private_key_file, public_key_file, sample_claims
  ):
    """
    Given: A valid token missing required claim
    When: Calling require_claims dependency
    Then: Should raise HTTPException with 403 status
    """
    from fastapi import HTTPException

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)
    toolkit.with_client_id(sample_claims.get("aud"))

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)
    dependency = oauth.require_claims(missing_claim="value")

    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = token

    request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
      await dependency(request, credentials)

    assert exc_info.value.status_code == 403
    assert "Missing required claim" in exc_info.value.detail

  @pytest.mark.asyncio
  async def test_require_claims_wrong_value_raises_403(
    self, private_key_file, public_key_file, sample_claims_with_extras
  ):
    """
    Given: A valid token with wrong claim value
    When: Calling require_claims dependency
    Then: Should raise HTTPException with 403 status
    """
    from fastapi import HTTPException

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims_with_extras)
    toolkit.with_client_id(sample_claims_with_extras.get("aud"))

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)
    dependency = oauth.require_claims(role="superadmin")

    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = token

    request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
      await dependency(request, credentials)

    assert exc_info.value.status_code == 403
    assert "Invalid value" in exc_info.value.detail

  @pytest.mark.asyncio
  async def test_require_claims_callable_validator_success(
    self, private_key_file, public_key_file, sample_claims_with_extras
  ):
    """
    Given: A valid token and callable validator
    When: Validator returns True
    Then: Should return claims
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims_with_extras)
    toolkit.with_client_id(sample_claims_with_extras.get("aud"))

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)
    dependency = oauth.require_claims(tier=lambda t: t in ["gold", "platinum"])

    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = token

    request = MagicMock()

    result = await dependency(request, credentials)

    assert result["tier"] == "gold"

  @pytest.mark.asyncio
  async def test_require_claims_callable_validator_failure(
    self, private_key_file, public_key_file, sample_claims_with_extras
  ):
    """
    Given: A valid token and callable validator
    When: Validator returns False
    Then: Should raise HTTPException with 403 status
    """
    from fastapi import HTTPException

    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims_with_extras)
    toolkit.with_client_id(sample_claims_with_extras.get("aud"))

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)
    dependency = oauth.require_claims(tier=lambda t: t == "platinum")

    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = token

    request = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
      await dependency(request, credentials)

    assert exc_info.value.status_code == 403
    assert "failed validation" in exc_info.value.detail

  @pytest.mark.asyncio
  async def test_require_claims_list_value_success(
    self, private_key_file, public_key_file, sample_claims_with_extras
  ):
    """
    Given: A valid token with list claim
    When: Required value is in the list
    Then: Should return claims
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims_with_extras)
    toolkit.with_client_id(sample_claims_with_extras.get("aud"))

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)
    # Check if "admin" is one of the allowed roles
    dependency = oauth.require_claims(roles=["admin", "superadmin"])

    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = token

    request = MagicMock()

    result = await dependency(request, credentials)

    assert "admin" in result["roles"]

  @pytest.mark.asyncio
  async def test_require_claims_multiple_claims(
    self, private_key_file, public_key_file, sample_claims_with_extras
  ):
    """
    Given: A valid token with multiple required claims
    When: All claims match
    Then: Should return claims
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims_with_extras)
    toolkit.with_client_id(sample_claims_with_extras.get("aud"))

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)
    dependency = oauth.require_claims(
      role="admin",
      tier="gold",
    )

    from unittest.mock import MagicMock

    credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    credentials.credentials = token

    request = MagicMock()

    result = await dependency(request, credentials)

    assert result["role"] == "admin"
    assert result["tier"] == "gold"


class TestFastAPIIntegration:
  """Integration tests with actual FastAPI app."""

  def test_fastapi_app_with_oauth(self, private_key_file, public_key_file):
    """
    Given: A FastAPI app with OAuthToolkitDependency
    When: Making authenticated requests
    Then: Should authenticate and authorize correctly
    """
    toolkit = AsyncOAuthToolkit()
    asyncio.get_event_loop().run_until_complete(
      toolkit.with_private(str(private_key_file))
    )
    asyncio.get_event_loop().run_until_complete(
      toolkit.with_public(str(public_key_file))
    )
    toolkit.claims(
      sub="test-user",
      iss="https://test.example.com",
      aud="test-client-id",
      role="admin",
      exp=int(time.time()) + 300,
    )
    toolkit.with_client_id("test-client-id")

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)

    app = FastAPI()

    @app.get("/protected")
    async def protected(user: dict = Depends(oauth.get_current_user)):
      return {"user_id": user["sub"]}

    @app.get("/admin")
    async def admin(user: dict = Depends(oauth.require_claims(role="admin"))):
      return {"admin_id": user["sub"]}

    client = TestClient(app)

    # Test without token
    response = client.get("/protected")
    assert response.status_code == 401  # Missing authorization (not authenticated)

    # Test with valid token
    response = client.get(
      "/protected",
      headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == "test-user"

    # Test admin endpoint with correct role
    response = client.get(
      "/admin",
      headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["admin_id"] == "test-user"

  def test_fastapi_app_rejects_wrong_claims(self, private_key_file, public_key_file):
    """
    Given: A FastAPI app with require_claims
    When: Token has wrong claim value
    Then: Should return 403
    """
    toolkit = AsyncOAuthToolkit()
    asyncio.get_event_loop().run_until_complete(
      toolkit.with_private(str(private_key_file))
    )
    asyncio.get_event_loop().run_until_complete(
      toolkit.with_public(str(public_key_file))
    )
    toolkit.claims(
      sub="test-user",
      iss="https://test.example.com",
      aud="test-client-id",
      role="user",  # Not admin
      exp=int(time.time()) + 300,
    )
    toolkit.with_client_id("test-client-id")

    token = toolkit.token

    oauth = OAuthToolkitDependency(toolkit)

    app = FastAPI()

    @app.get("/admin")
    async def admin(user: dict = Depends(oauth.require_claims(role="admin"))):
      return {"admin_id": user["sub"]}

    client = TestClient(app)

    # Test with wrong role
    response = client.get(
      "/admin",
      headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "Invalid value" in response.json()["detail"]
