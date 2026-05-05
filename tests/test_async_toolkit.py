"""
Test suite for AsyncOAuthToolkit class.

Tests verify:
- AsyncOAuthToolkit instantiation
- Async key loading (with_private, with_public)
- Async provider initialization (using_provider, init_from_provider)
- Async JWKS loading
- Token generation (sync)
- Async token validation
- Async file operations
- Method chaining
"""

import json
import tempfile
from pathlib import Path

import pytest
import jwt

from oatk.async_toolkit import AsyncOAuthToolkit


class TestAsyncOAuthToolkitInstantiation:
  """Test AsyncOAuthToolkit class instantiation."""

  def test_create_async_oauth_toolkit_instance(self):
    """
    Given: The AsyncOAuthToolkit class
    When: Creating a new instance
    Then: Instance should be created with default values
    """
    toolkit = AsyncOAuthToolkit()
    assert toolkit is not None, "Should create AsyncOAuthToolkit instance"
    assert toolkit._encoded is None, "Encoded should be None initially"
    assert toolkit._provider_url is None, "Provider URL should be None initially"
    assert toolkit._certs == {}, "Certs should be empty dict initially"
    assert toolkit._private_key is None, "Private key should be None initially"
    assert toolkit._public_key is None, "Public key should be None initially"
    assert toolkit._alg == "RS256", "Algorithm should be RS256"
    assert toolkit._client_id is None, "Client ID should be None initially"

  def test_async_oauth_toolkit_has_server_attribute(self):
    """
    Given: An AsyncOAuthToolkit instance
    When: Accessing the server attribute
    Then: Should have a server attribute for fake OAuth server
    """
    toolkit = AsyncOAuthToolkit()
    assert hasattr(toolkit, "server"), "Should have server attribute"


class TestAsyncOAuthToolkitKeyLoading:
  """Test AsyncOAuthToolkit async key loading methods."""

  @pytest.mark.asyncio
  async def test_with_private_loads_key(self, private_key_file):
    """
    Given: An AsyncOAuthToolkit instance and a private key file
    When: Calling with_private() asynchronously
    Then: Should load the private key and return self
    """
    toolkit = AsyncOAuthToolkit()
    result = await toolkit.with_private(str(private_key_file))

    assert result is toolkit, "Should return self for method chaining"
    assert toolkit._private_key is not None, "Should load private key"

  @pytest.mark.asyncio
  async def test_with_public_loads_key(self, public_key_file):
    """
    Given: An AsyncOAuthToolkit instance and a public key file
    When: Calling with_public() asynchronously
    Then: Should load the public key and return self
    """
    toolkit = AsyncOAuthToolkit()
    result = await toolkit.with_public(str(public_key_file))

    assert result is toolkit, "Should return self for method chaining"
    assert toolkit._public_key is not None, "Should load public key"
    assert toolkit._kid in toolkit._certs, "Should add public key to certs"

  @pytest.mark.asyncio
  async def test_with_private_chains_to_with_public(self, private_key_file, public_key_file):
    """
    Given: An AsyncOAuthToolkit instance
    When: Chaining with_private() and with_public()
    Then: Should load both keys
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file)).with_public(str(public_key_file))

    assert toolkit._private_key is not None, "Should load private key"
    assert toolkit._public_key is not None, "Should load public key"


class TestAsyncOAuthToolkitProviderInit:
  """Test AsyncOAuthToolkit async provider initialization."""

  @pytest.mark.asyncio
  async def test_using_provider_fetches_configuration(self, httpx_mock):
    """
    Given: A mock OAuth provider
    When: Calling using_provider() asynchronously
    Then: Should fetch OpenID configuration and JWKS
    """
    openid_config = {
      "issuer": "https://example.com",
      "jwks_uri": "https://example.com/oauth/certs",
      "token_endpoint": "https://example.com/oauth/token",
    }

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
      url="https://example.com/.well-known/openid-configuration",
      json=openid_config,
      status_code=200,
    )
    httpx_mock.add_response(
      url="https://example.com/oauth/certs",
      json=jwks,
      status_code=200,
    )

    toolkit = AsyncOAuthToolkit()
    result = await toolkit.using_provider(
      "https://example.com/.well-known/openid-configuration"
    )

    assert result is toolkit, "Should return self for method chaining"
    assert toolkit._provider_url == "https://example.com/.well-known/openid-configuration"
    assert "test-key-id" in toolkit._certs, "Should load JWKS keys"

  @pytest.mark.asyncio
  async def test_init_from_provider_requires_provider_url(self):
    """
    Given: An AsyncOAuthToolkit instance without provider URL
    When: Calling init_from_provider()
    Then: Should raise ValueError
    """
    toolkit = AsyncOAuthToolkit()

    with pytest.raises(ValueError, match="missing provider url"):
      await toolkit.init_from_provider()

  @pytest.mark.asyncio
  async def test_init_from_provider_handles_http_error(self, httpx_mock):
    """
    Given: A provider URL that returns an error
    When: Calling init_from_provider()
    Then: Should return None and log error
    """
    httpx_mock.add_response(
      url="https://example.com/.well-known/openid-configuration",
      status_code=500,
    )

    toolkit = AsyncOAuthToolkit()
    toolkit._provider_url = "https://example.com/.well-known/openid-configuration"

    result = await toolkit.init_from_provider()

    assert result is None, "Should return None on error"


class TestAsyncOAuthToolkitJWKS:
  """Test AsyncOAuthToolkit JWKS handling."""

  @pytest.mark.asyncio
  async def test_with_jwks_from_dict(self, jwks_dict):
    """
    Given: An AsyncOAuthToolkit instance and a JWKS dictionary
    When: Calling with_jwks() with a dict
    Then: Should load the JWKS keys
    """
    toolkit = AsyncOAuthToolkit()
    result = await toolkit.with_jwks(jwks_dict)

    assert result is toolkit, "Should return self for method chaining"
    assert len(toolkit._certs) == 1, "Should have one key"
    assert toolkit._kid in toolkit._certs, "Should have key with correct kid"

  @pytest.mark.asyncio
  async def test_with_jwks_from_json_string(self, jwks_json):
    """
    Given: An AsyncOAuthToolkit instance and a JWKS JSON string
    When: Calling with_jwks() with a JSON string
    Then: Should parse and load the JWKS keys
    """
    toolkit = AsyncOAuthToolkit()
    result = await toolkit.with_jwks(jwks_json)

    assert result is toolkit, "Should return self for method chaining"
    assert len(toolkit._certs) == 1, "Should have one key"

  @pytest.mark.asyncio
  async def test_with_jwks_from_file(self, jwks_file):
    """
    Given: An AsyncOAuthToolkit instance and a JWKS file path
    When: Calling with_jwks() with a file path
    Then: Should read the file asynchronously and load JWKS
    """
    toolkit = AsyncOAuthToolkit()
    result = await toolkit.with_jwks(str(jwks_file))

    assert result is toolkit, "Should return self for method chaining"
    assert len(toolkit._certs) == 1, "Should have one key"

  @pytest.mark.asyncio
  async def test_with_jwks_from_bytes(self, jwks_json):
    """
    Given: An AsyncOAuthToolkit instance and JWKS as bytes
    When: Calling with_jwks() with bytes
    Then: Should parse and load the JWKS keys
    """
    toolkit = AsyncOAuthToolkit()
    result = await toolkit.with_jwks(jwks_json.encode())

    assert result is toolkit, "Should return self for method chaining"
    assert len(toolkit._certs) == 1, "Should have one key"


class TestAsyncOAuthToolkitClaims:
  """Test AsyncOAuthToolkit claims methods."""

  def test_claims_sets_claims(self):
    """
    Given: An AsyncOAuthToolkit instance
    When: Calling claims() with claims
    Then: Should set the claims
    """
    toolkit = AsyncOAuthToolkit()
    result = toolkit.claims(sub="test-user", iss="https://example.com")

    assert result is toolkit, "Should return self for method chaining"
    assert toolkit._claims["sub"] == "test-user"
    assert toolkit._claims["iss"] == "https://example.com"

  def test_claims_with_dict(self):
    """
    Given: An AsyncOAuthToolkit instance
    When: Calling claims() with a dictionary
    Then: Should set the claims from dict
    """
    toolkit = AsyncOAuthToolkit()
    result = toolkit.claims({"sub": "test-user", "iss": "https://example.com"})

    assert result is toolkit, "Should return self for method chaining"
    assert toolkit._claims["sub"] == "test-user"
    assert toolkit._claims["iss"] == "https://example.com"

  def test_claims_merges_dicts(self):
    """
    Given: An AsyncOAuthToolkit instance
    When: Calling claims() with dict and kwargs
    Then: Should merge both sources
    """
    toolkit = AsyncOAuthToolkit()
    result = toolkit.claims(
      {"sub": "test-user", "iss": "https://example.com"},
      aud="my-client-id",
    )

    assert result is toolkit, "Should return self for method chaining"
    assert toolkit._claims["sub"] == "test-user"
    assert toolkit._claims["iss"] == "https://example.com"
    assert toolkit._claims["aud"] == "my-client-id"


class TestAsyncOAuthToolkitToken:
  """Test AsyncOAuthToolkit token generation."""

  @pytest.mark.asyncio
  async def test_token_generation_with_private_key(self, private_key_file, public_key_file):
    """
    Given: An AsyncOAuthToolkit with private key and claims
    When: Accessing the token property
    Then: Should generate a valid JWT token
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(sub="test-user", iss="https://example.com")

    token = toolkit.token

    assert token is not None, "Should generate token"
    assert isinstance(token, str), "Token should be string"
    # Verify the token can be decoded
    header = toolkit.header(token)
    assert header["alg"] == "RS256"
    assert "kid" in header

  @pytest.mark.asyncio
  async def test_token_returns_none_without_private_key(self):
    """
    Given: An AsyncOAuthToolkit without private key
    When: Accessing the token property
    Then: Should return None
    """
    toolkit = AsyncOAuthToolkit()
    toolkit.claims(sub="test-user")

    token = toolkit.token

    assert token is None, "Should return None without private key"

  @pytest.mark.asyncio
  async def test_token_uses_configured_claims(self, private_key_file, public_key_file):
    """
    Given: An AsyncOAuthToolkit with custom claims
    When: Generating a token
    Then: Token should contain the custom claims
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(sub="test-user", custom_claim="custom_value")

    token = toolkit.token
    decoded = toolkit.decode(token)

    assert decoded["sub"] == "test-user"
    assert decoded["custom_claim"] == "custom_value"


class TestAsyncOAuthToolkitValidation:
  """Test AsyncOAuthToolkit async token validation."""

  @pytest.mark.asyncio
  async def test_validate_token_with_public_key(self, private_key_file, public_key_file, sample_claims):
    """
    Given: An AsyncOAuthToolkit with public key and a valid token
    When: Calling validate() asynchronously
    Then: Should validate and return claims
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.claims(**sample_claims)

    token = toolkit.token
    validated = await toolkit.validate(token)

    assert validated["sub"] == sample_claims["sub"]
    assert validated["iss"] == sample_claims["iss"]

  @pytest.mark.asyncio
  async def test_validate_token_with_jwks(self, jwks_dict, rsa_key_pair, sample_claims):
    """
    Given: An AsyncOAuthToolkit with JWKS and a valid token
    When: Calling validate() asynchronously
    Then: Should validate using JWKS keys
    """
    from oatk import OAuthToolkit

    # Create a token with the sync toolkit using the key pair
    sync_toolkit = OAuthToolkit()
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem') as f:
      f.write(rsa_key_pair['private_key'])
      private_key_path = f.name

    sync_toolkit.with_private(private_key_path)
    sync_toolkit.claims(**sample_claims)
    token = sync_toolkit.token

    # Validate with async toolkit using JWKS
    async_toolkit = AsyncOAuthToolkit()
    await async_toolkit.with_jwks(jwks_dict)

    validated = await async_toolkit.validate(token)

    assert validated["sub"] == sample_claims["sub"]

  @pytest.mark.asyncio
  async def test_validate_token_with_audience(self, private_key_file, public_key_file):
    """
    Given: An AsyncOAuthToolkit with client_id and a token with audience
    When: Validating the token
    Then: Should validate audience correctly
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    await toolkit.with_public(str(public_key_file))
    toolkit.with_client_id("my-client-id")
    toolkit.claims(sub="test-user", aud="my-client-id")

    token = toolkit.token
    validated = await toolkit.validate(token)

    assert validated["aud"] == "my-client-id"


class TestAsyncOAuthToolkitFileOperations:
  """Test AsyncOAuthToolkit async file operations."""

  @pytest.mark.asyncio
  async def test_from_file_loads_token(self, tmp_path):
    """
    Given: A file containing a token
    When: Calling from_file() asynchronously
    Then: Should load the token
    """
    token_content = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"
    token_file = tmp_path / "token.txt"
    token_file.write_text(token_content)

    toolkit = AsyncOAuthToolkit()
    result = await toolkit.from_file(str(token_file))

    assert result is toolkit, "Should return self for method chaining"
    assert toolkit._encoded == token_content

  @pytest.mark.asyncio
  async def test_from_file_strips_whitespace(self, tmp_path):
    """
    Given: A file containing a token with trailing newline
    When: Calling from_file()
    Then: Should strip whitespace
    """
    token_content = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test\n"
    token_file = tmp_path / "token.txt"
    token_file.write_text(token_content)

    toolkit = AsyncOAuthToolkit()
    await toolkit.from_file(str(token_file))

    assert toolkit._encoded == "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"


class TestAsyncOAuthToolkitDecode:
  """Test AsyncOAuthToolkit decode method."""

  @pytest.mark.asyncio
  async def test_decode_token_without_validation(self, private_key_file, public_key_file):
    """
    Given: An AsyncOAuthToolkit and a token
    When: Calling decode() without public key
    Then: Should decode without signature validation
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    toolkit.claims(sub="test-user", iss="https://example.com")

    token = toolkit.token
    decoded = toolkit.decode(token)

    assert decoded["sub"] == "test-user"
    assert decoded["iss"] == "https://example.com"

  def test_decode_uses_loaded_token(self):
    """
    Given: An AsyncOAuthToolkit with a loaded token
    When: Calling decode() without argument
    Then: Should decode the loaded token
    """
    toolkit = AsyncOAuthToolkit()
    toolkit._encoded = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.signature"

    decoded = toolkit.decode()

    assert decoded["sub"] == "test"


class TestAsyncOAuthToolkitMethodChaining:
  """Test AsyncOAuthToolkit method chaining pattern."""

  @pytest.mark.asyncio
  async def test_chaining_multiple_methods(self, private_key_file, public_key_file, sample_claims):
    """
    Given: An AsyncOAuthToolkit instance
    When: Chaining multiple methods
    Then: Should return self for each method
    """
    toolkit = AsyncOAuthToolkit()

    result = await (
      toolkit
      .with_private(str(private_key_file))
      .with_public(str(public_key_file))
      .claims(**sample_claims)
      .with_client_id("test-client-id")
    )

    assert result is toolkit, "Should return self after chaining"
    assert toolkit._private_key is not None
    assert toolkit._public_key is not None
    assert toolkit._claims == sample_claims
    assert toolkit._client_id == "test-client-id"


class TestAsyncOAuthToolkitJWKSProperty:
  """Test AsyncOAuthToolkit JWKS property."""

  @pytest.mark.asyncio
  async def test_jwks_property_returns_json(self, public_key_file):
    """
    Given: An AsyncOAuthToolkit with public key
    When: Accessing jwks property
    Then: Should return JWKS JSON string
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_public(str(public_key_file))

    jwks = toolkit.jwks

    assert isinstance(jwks, str)
    jwks_dict = json.loads(jwks)
    assert "keys" in jwks_dict
    assert len(jwks_dict["keys"]) == 1
    assert jwks_dict["keys"][0]["kty"] == "RSA"
    assert jwks_dict["keys"][0]["alg"] == "RS256"


class TestAsyncOAuthToolkitHeader:
  """Test AsyncOAuthToolkit header method."""

  @pytest.mark.asyncio
  async def test_header_extracts_jwt_header(self, private_key_file):
    """
    Given: An AsyncOAuthToolkit with a token
    When: Calling header()
    Then: Should extract the JWT header
    """
    toolkit = AsyncOAuthToolkit()
    await toolkit.with_private(str(private_key_file))
    toolkit.claims(sub="test-user")

    token = toolkit.token
    header = toolkit.header(token)

    assert header["alg"] == "RS256"
    assert "kid" in header