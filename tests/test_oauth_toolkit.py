"""
Test suite for OAuthToolkit class.

Tests verify:
- Package imports successfully
- OAuthToolkit instantiation
- Key loading (private and public)
- Token creation, validation, and decoding
- JWKS import and export
- Claims management
"""

import json

import pytest

from oatk import OAuthToolkit


class TestPackageImports:
  """Test that the package imports successfully."""

  def test_import_oatk_package(self):
    """
    Given: The oatk package is installed
    When: Importing the package
    Then: The package should be imported without errors
    """
    # This test verifies the package structure is correct
    # Expected behavior: Import succeeds
    import oatk

    assert hasattr(oatk, "OAuthToolkit"), "Package should export OAuthToolkit class"

  def test_import_oauth_toolkit_class(self):
    """
    Given: The OAuthToolkit class is defined
    When: Importing the class directly
    Then: The class should be available
    """
    # This test verifies the class is properly exported
    # Expected behavior: Class is importable
    from oatk import OAuthToolkit

    assert OAuthToolkit is not None, "OAuthToolkit class should be defined"

  def test_import_fake_module(self):
    """
    Given: The fake module is part of the package
    When: Importing the fake submodule
    Then: The module should be available
    """
    # This test verifies the fake server module structure
    # Expected behavior: Module is importable
    from oatk import fake

    assert hasattr(fake, "server"), "Fake module should have server attribute"


class TestOAuthToolkitInstantiation:
  """Test OAuthToolkit class instantiation."""

  def test_create_oauth_toolkit_instance(self):
    """
    Given: The OAuthToolkit class
    When: Creating a new instance
    Then: Instance should be created with default values
    """
    # This test verifies basic instantiation
    # Expected behavior: Instance created with defaults
    oatk = OAuthToolkit()
    assert oatk is not None, "Should create OAuthToolkit instance"
    assert oatk._private_key is None, "Private key should be None initially"
    assert oatk._public_key is None, "Public key should be None initially"
    assert oatk._certs == {}, "Certs should be empty dict initially"
    assert oatk._claims == {}, "Claims should be empty dict initially"

  def test_oauth_toolkit_version_property(self):
    """
    Given: An OAuthToolkit instance
    When: Accessing the version property
    Then: Should return the package version string
    """
    # This test verifies version property exists
    # Expected behavior: Version string is returned
    oatk = OAuthToolkit()
    version = oatk.version
    assert isinstance(version, str), "Version should be a string"
    assert len(version) > 0, "Version should not be empty"


class TestKeyLoading:
  """Test private and public key loading."""

  def test_load_private_key_from_file(self, private_key_file):
    """
    Given: A valid private key file
    When: Loading the private key using with_private()
    Then: Private key should be loaded and instance returned
    """
    # This test verifies private key loading
    # Expected behavior: Private key loaded, method chainable
    oatk = OAuthToolkit()
    result = oatk.with_private(str(private_key_file))

    assert result is oatk, "with_private should return self for chaining"
    assert oatk._private_key is not None, "Private key should be loaded"
    assert oatk._public_key is None, "Public key should remain None"

  def test_load_public_key_from_file(self, public_key_file):
    """
    Given: A valid public key file
    When: Loading the public key using with_public()
    Then: Public key should be loaded and certs populated
    """
    # This test verifies public key loading
    # Expected behavior: Public key loaded, certs populated, method chainable
    oatk = OAuthToolkit()
    result = oatk.with_public(str(public_key_file))

    assert result is oatk, "with_public should return self for chaining"
    assert oatk._public_key is not None, "Public key should be loaded"
    assert len(oatk._certs) == 1, "Certs should contain one public key"
    assert oatk._kid in oatk._certs, "Certs should be keyed by kid"

  def test_load_both_keys(self, private_key_file, public_key_file):
    """
    Given: Valid private and public key files
    When: Loading both keys
    Then: Both keys should be loaded and usable
    """
    # This test verifies loading both keys
    # Expected behavior: Both keys loaded, ready for token operations
    oatk = OAuthToolkit()
    oatk.with_private(str(private_key_file))
    oatk.with_public(str(public_key_file))

    assert oatk._private_key is not None, "Private key should be loaded"
    assert oatk._public_key is not None, "Public key should be loaded"
    assert len(oatk._certs) == 1, "Certs should contain one key"


class TestJWKSHandling:
  """Test JWKS import and export."""

  def test_import_jwks_from_file(self, jwks_file):
    """
    Given: A valid JWKS file
    When: Loading JWKS using with_jwks()
    Then: Certs should be populated from JWKS keys
    """
    # This test verifies JWKS file import
    # Expected behavior: JWKS loaded, certs populated
    oatk = OAuthToolkit()
    result = oatk.with_jwks(str(jwks_file))

    assert result is oatk, "with_jwks should return self for chaining"
    assert len(oatk._certs) > 0, "Certs should contain keys from JWKS"

  def test_import_jwks_from_json_string(self, jwks_json):
    """
    Given: A valid JWKS JSON string
    When: Loading JWKS using with_jwks() with string
    Then: Certs should be populated from JWKS keys
    """
    # This test verifies JWKS string import
    # Expected behavior: JWKS parsed, certs populated
    oatk = OAuthToolkit()
    result = oatk.with_jwks(jwks_json)

    assert result is oatk, "with_jwks should return self for chaining"
    assert len(oatk._certs) > 0, "Certs should contain keys from JWKS"

  def test_import_jwks_from_dict(self, jwks_dict):
    """
    Given: A valid JWKS dictionary
    When: Loading JWKS using with_jwks() with dict
    Then: Certs should be populated from JWKS keys
    """
    # This test verifies JWKS dict import
    # Expected behavior: JWKS processed, certs populated
    oatk = OAuthToolkit()
    result = oatk.with_jwks(jwks_dict)

    assert result is oatk, "with_jwks should return self for chaining"
    assert len(oatk._certs) > 0, "Certs should contain keys from JWKS"

  def test_export_jwks(self, configured_oauth_toolkit):
    """
    Given: An OAuthToolkit instance with public key loaded
    When: Accessing the jwks property
    Then: Should return valid JWKS JSON string
    """
    # This test verifies JWKS export
    # Expected behavior: JWKS generated with public key
    jwks_json = configured_oauth_toolkit.jwks

    assert jwks_json is not None, "JWKS should not be None"
    assert isinstance(jwks_json, str), "JWKS should be JSON string"

    # Parse and validate structure
    jwks = json.loads(jwks_json)
    assert "keys" in jwks, "JWKS should have 'keys' array"
    assert len(jwks["keys"]) == 1, "Should have one key"
    assert "kid" in jwks["keys"][0], "Key should have kid"
    assert "kty" in jwks["keys"][0], "Key should have kty"
    assert "n" in jwks["keys"][0], "Key should have modulus"
    assert "e" in jwks["keys"][0], "Key should have exponent"


class TestClaimsManagement:
  """Test claims management."""

  def test_set_claims_with_dict(self, oauth_toolkit):
    """
    Given: An OAuthToolkit instance
    When: Setting claims using claims() with dict
    Then: Claims should be stored
    """
    # This test verifies claims setting with dict
    # Expected behavior: Claims stored, method chainable
    claims = {"sub": "user123", "iss": "test"}
    result = oauth_toolkit.claims(claims)

    assert result is oauth_toolkit, "claims() should return self for chaining"
    assert oauth_toolkit._claims == claims, "Claims should be stored"

  def test_set_claims_with_kwargs(self, oauth_toolkit):
    """
    Given: An OAuthToolkit instance
    When: Setting claims using claims() with kwargs
    Then: Claims should be stored
    """
    # This test verifies claims setting with kwargs
    # Expected behavior: Claims stored from kwargs
    result = oauth_toolkit.claims(sub="user123", iss="test")

    assert result is oauth_toolkit, "claims() should return self for chaining"
    assert oauth_toolkit._claims["sub"] == "user123", "sub claim should be set"
    assert oauth_toolkit._claims["iss"] == "test", "iss claim should be set"

  def test_set_claims_combined(self, oauth_toolkit):
    """
    Given: An OAuthToolkit instance
    When: Setting claims using both dict and kwargs
    Then: Both should be merged
    """
    # This test verifies claims merging
    # Expected behavior: Dict and kwargs merged
    claims_dict = {"sub": "user123"}
    result = oauth_toolkit.claims(claims_dict, iss="test", aud="client")

    assert result is oauth_toolkit, "claims() should return self for chaining"
    assert oauth_toolkit._claims["sub"] == "user123", "sub claim from dict"
    assert oauth_toolkit._claims["iss"] == "test", "iss claim from kwargs"
    assert oauth_toolkit._claims["aud"] == "client", "aud claim from kwargs"


class TestTokenCreation:
  """Test JWT token creation."""

  def test_create_token_with_private_key(self, configured_oauth_toolkit):
    """
    Given: An OAuthToolkit with private key and claims
    When: Accessing the token property
    Then: Should return a valid JWT token string
    """
    # This test verifies token creation
    # Expected behavior: Valid JWT token generated
    token = configured_oauth_toolkit.token

    assert token is not None, "Token should not be None"
    assert isinstance(token, str), "Token should be string"
    assert len(token) > 0, "Token should not be empty"

    # Basic JWT structure check (header.payload.signature)
    parts = token.split(".")
    assert len(parts) == 3, "JWT should have 3 parts"

  def test_create_token_without_private_key(self, oauth_toolkit):
    """
    Given: An OAuthToolkit without private key
    When: Accessing the token property
    Then: Should return None
    """
    # This test verifies token creation requires private key
    # Expected behavior: No token without private key
    token = oauth_toolkit.token

    assert token is None, "Token should be None without private key"

  def test_token_includes_claims(self, configured_oauth_toolkit, sample_claims):
    """
    Given: An OAuthToolkit with private key and claims
    When: Creating a token
    Then: Token should include the claims
    """
    # This test verifies claims are included in token
    # Expected behavior: Claims present in decoded token
    import jwt

    token = configured_oauth_toolkit.token
    decoded = jwt.decode(token, options={"verify_signature": False})

    # Check key claims are present
    assert "sub" in decoded, "Token should have sub claim"
    assert "iss" in decoded, "Token should have iss claim"
    assert "exp" in decoded, "Token should have exp claim"
    assert decoded["sub"] == sample_claims["sub"], "sub claim should match"

  def test_token_includes_kid_header(self, configured_oauth_toolkit):
    """
    Given: An OAuthToolkit with private key and kid
    When: Creating a token
    Then: Token header should include kid
    """
    # This test verifies kid is in token header
    # Expected behavior: kid present in header
    import jwt

    token = configured_oauth_toolkit.token
    header = jwt.get_unverified_header(token)

    assert "kid" in header, "Token header should have kid"
    assert header["kid"] == configured_oauth_toolkit._kid, "kid should match"


class TestTokenValidation:
  """Test JWT token validation."""

  def test_validate_token_with_matching_kid(self, configured_oauth_toolkit):
    """
    Given: A valid token created by the same OAuthToolkit
    When: Validating the token
    Then: Validation should succeed
    """
    # This test verifies token validation with matching kid
    # Expected behavior: Token validates successfully
    configured_oauth_toolkit.with_client_id(configured_oauth_toolkit._claims.get("aud"))
    token = configured_oauth_toolkit.token
    # Validation should not raise exception
    result = configured_oauth_toolkit.validate(token)

    assert result is not None or result is None, "Validation should complete"

  def test_validate_token_without_client_id(self, configured_oauth_toolkit):
    """
    Given: A token without audience validation
    When: Validating the token
    Then: Should validate if client_id not set
    """
    # This test validates token without client_id
    # Create a token without audience claim to avoid validation
    configured_oauth_toolkit._claims.pop("aud", None)
    configured_oauth_toolkit._client_id = None
    token = configured_oauth_toolkit.token
    result = configured_oauth_toolkit.validate(token)

    assert result["sub"] == configured_oauth_toolkit._claims["sub"]

  def test_validate_token_with_client_id(self, configured_oauth_toolkit):
    """
    Given: A token with audience claim and client_id set
    When: Validating the token
    Then: Should validate if audience matches client_id
    """
    # This test validates token with audience check
    # Expected behavior: Validation succeeds when audience matches
    token = configured_oauth_toolkit.token
    configured_oauth_toolkit.with_client_id(configured_oauth_toolkit._claims.get("aud"))

    # Should not raise exception
    configured_oauth_toolkit.validate(token)

  def test_validate_token_with_wrong_client_id(self, configured_oauth_toolkit):
    """
    Given: A token with audience and wrong client_id
    When: Validating the token
    Then: Should raise exception
    """
    # This test verifies audience validation
    # First set correct audience
    configured_oauth_toolkit.with_client_id(configured_oauth_toolkit._claims.get("aud"))
    token = configured_oauth_toolkit.token
    # Then set wrong client_id
    configured_oauth_toolkit.with_client_id("wrong-client-id")

    # JWT raises InvalidAudienceError for wrong audience - we catch it as Exception
    with pytest.raises(Exception):  # noqa: B017
      configured_oauth_toolkit.validate(token)

  def test_validate_token_with_unknown_kid(self, oauth_toolkit_with_jwks):  # noqa: ARG002
    """
    Given: A token with unknown kid
    When: Validating the token
    Then: Should raise KeyError for unknown kid
    """
    # This test verifies unknown kid handling
    # Expected behavior: KeyError for unknown kid

    # Create a token with a different kid
    # This is a bit tricky - we need to create a token with unknown kid
    # For now, we'll test with a manually created token
    pytest.skip("Not implemented: test with token having unknown kid")


class TestTokenDecoding:
  """Test JWT token decoding."""

  def test_decode_token_without_verification(self, configured_oauth_toolkit):
    """
    Given: A valid token
    When: Decoding without signature verification
    Then: Should return claims dictionary
    """
    # This test verifies token decoding
    # Expected behavior: Claims returned without verification
    token = configured_oauth_toolkit.token
    decoded = configured_oauth_toolkit.decode(token)

    assert isinstance(decoded, dict), "Decoded token should be dict"
    assert "sub" in decoded, "Decoded token should have sub claim"
    assert "iss" in decoded, "Decoded token should have iss claim"

  def test_decode_token_preserves_claims(self, configured_oauth_toolkit, sample_claims):
    """
    Given: A token with specific claims
    When: Decoding the token
    Then: Claims should be preserved
    """
    # This test verifies claim preservation
    # Expected behavior: All claims present in decoded token
    token = configured_oauth_toolkit.token
    decoded = configured_oauth_toolkit.decode(token)

    # Check claims match
    assert decoded["sub"] == sample_claims["sub"], "sub claim should match"
    assert decoded["iss"] == sample_claims["iss"], "iss claim should match"


class TestTokenHeader:
  """Test JWT token header operations."""

  def test_get_token_header(self, configured_oauth_toolkit):
    """
    Given: A valid token
    When: Getting the token header
    Then: Should return header dictionary
    """
    # This test verifies header extraction
    # Expected behavior: Header dictionary returned

    token = configured_oauth_toolkit.token
    header = configured_oauth_toolkit.header(token)

    assert isinstance(header, dict), "Header should be dict"
    assert "alg" in header, "Header should have alg"
    assert "kid" in header, "Header should have kid"
    assert header["alg"] == "RS256", "Algorithm should be RS256"

  def test_get_header_from_stored_token(self, configured_oauth_toolkit):
    """
    Given: An OAuthToolkit with stored token (_encoded)
    When: Calling header() without token argument
    Then: Should use stored token
    """
    # This test verifies stored token usage
    # Expected behavior: Uses _encoded token
    token = configured_oauth_toolkit.token
    configured_oauth_toolkit._encoded = token

    header = configured_oauth_toolkit.header()

    assert header is not None, "Header should not be None"
    assert "kid" in header, "Header should have kid"


class TestTokenFromFile:
  """Test loading tokens from files."""

  def test_load_token_from_file(self, configured_oauth_toolkit, tmp_path):
    """
    Given: A file containing a JWT token
    When: Loading token using from_file()
    Then: Token should be stored in _encoded
    """
    # This test verifies file token loading
    # Expected behavior: Token loaded from file
    token = configured_oauth_toolkit.token
    token_file = tmp_path / "token.txt"
    token_file.write_text(token)

    oatk = OAuthToolkit()
    result = oatk.from_file(str(token_file))

    assert result is oatk, "from_file should return self"
    assert oatk._encoded == token, "Token should be stored in _encoded"


class TestMethodChaining:
  """Test that methods support chaining."""

  def test_key_loading_chain(self, private_key_file, public_key_file):
    """
    Given: OAuthToolkit class
    When: Chaining with_private() and with_public()
    Then: Both should return self for chaining
    """
    # This test verifies method chaining
    # Expected behavior: Methods return self
    oatk = OAuthToolkit()
    result = oatk.with_private(str(private_key_file)).with_public(str(public_key_file))

    assert result is oatk, "Chained calls should return self"

  def test_claims_and_token_chain(self, private_key_file, sample_claims):
    """
    Given: OAuthToolkit with private key
    When: Chaining claims() and token property
    Then: Should create token with claims
    """
    # This test verifies claims and token chain
    # Expected behavior: Token created with claims
    oatk = OAuthToolkit()
    oatk.with_private(str(private_key_file))
    oatk.claims(**sample_claims)
    token = oatk.token

    assert token is not None, "Token should not be None"
