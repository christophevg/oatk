"""
Common pytest fixtures for oatk test suite.

This module provides reusable test fixtures for:
- RSA key pair generation and loading
- JWKS (JSON Web Key Set) creation
- OAuthToolkit instances
- Sample JWT claims
"""

import json

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from oatk import OAuthToolkit


@pytest.fixture
def rsa_key_pair():
  """
  Generate an RSA key pair for testing.

  Returns:
      dict: Dictionary containing 'private_key' and 'public_key' as
            PEM-encoded bytes
  """
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

  return {
    "private_key": private_pem,
    "public_key": public_pem,
    "private_key_obj": private_key,
    "public_key_obj": public_key,
  }


@pytest.fixture
def private_key_file(rsa_key_pair, tmp_path):
  """
  Create a temporary file containing the private key.

  Args:
      rsa_key_pair: Fixture providing RSA key pair
      tmp_path: pytest temporary path fixture

  Returns:
      Path: Path to temporary private key file
  """
  key_file = tmp_path / "private_key.pem"
  key_file.write_bytes(rsa_key_pair["private_key"])
  return key_file


@pytest.fixture
def public_key_file(rsa_key_pair, tmp_path):
  """
  Create a temporary file containing the public key.

  Args:
      rsa_key_pair: Fixture providing RSA key pair
      tmp_path: pytest temporary path fixture

  Returns:
      Path: Path to temporary public key file
  """
  key_file = tmp_path / "public_key.pem"
  key_file.write_bytes(rsa_key_pair["public_key"])
  return key_file


@pytest.fixture
def sample_claims():
  """
  Provide sample JWT claims for testing.

  Returns:
      dict: Sample claims dictionary
  """
  import time
  import uuid

  now = int(time.time())
  return {
    "iat": now,
    "exp": now + 300,  # 5 minutes expiration
    "iss": "https://test.example.com",
    "sub": f"test-user-{str(uuid.uuid4())}",
    "aud": "test-client-id",
    "scope": "openid profile email",
    "username": "testuser",
    "email": "testuser@example.com",
  }


@pytest.fixture
def jwks_dict(rsa_key_pair):
  """
  Create a JWKS dictionary from the RSA key pair.

  Args:
      rsa_key_pair: Fixture providing RSA key pair

  Returns:
      dict: JWKS dictionary with keys array
  """
  import uuid

  from authlib.jose import jwk

  kid = str(uuid.uuid4())
  public_key = rsa_key_pair["public_key_obj"]

  # Convert public key to JWK format
  # jwk.dumps returns a dict, not a JSON string
  jwk_dict = jwk.dumps(public_key, kty="RSA", alg="RS256", kid=kid)

  return {"keys": [jwk_dict]}


@pytest.fixture
def jwks_json(jwks_dict):
  """
  Create a JWKS JSON string.

  Args:
      jwks_dict: Fixture providing JWKS dictionary

  Returns:
      str: JSON string of JWKS
  """
  return json.dumps(jwks_dict)


@pytest.fixture
def jwks_file(jwks_dict, tmp_path):
  """
  Create a temporary file containing JWKS.

  Args:
      jwks_dict: Fixture providing JWKS dictionary
      tmp_path: pytest temporary path fixture

  Returns:
      Path: Path to temporary JWKS file
  """
  jwks_file = tmp_path / "jwks.json"
  jwks_file.write_text(json.dumps(jwks_dict))
  return jwks_file


@pytest.fixture
def oauth_toolkit():
  """
  Create a basic OAuthToolkit instance.

  Returns:
      OAuthToolkit: New OAuthToolkit instance
  """
  return OAuthToolkit()


@pytest.fixture
def configured_oauth_toolkit(private_key_file, public_key_file, sample_claims):
  """
  Create a fully configured OAuthToolkit instance with keys and claims.

  Args:
      private_key_file: Fixture providing private key file path
      public_key_file: Fixture providing public key file path
      sample_claims: Fixture providing sample claims

  Returns:
      OAuthToolkit: Configured OAuthToolkit instance
  """
  oatk = OAuthToolkit()
  oatk.with_private(str(private_key_file))
  oatk.with_public(str(public_key_file))
  oatk.claims(**sample_claims)
  return oatk


@pytest.fixture
def oauth_toolkit_with_jwks(jwks_file):
  """
  Create an OAuthToolkit instance configured from JWKS.

  Args:
      jwks_file: Fixture providing JWKS file path

  Returns:
      OAuthToolkit: OAuthToolkit instance configured with JWKS
  """
  oatk = OAuthToolkit()
  oatk.with_jwks(str(jwks_file))
  return oatk


@pytest.fixture
def valid_token(configured_oauth_toolkit):
  """
  Create a valid JWT token using the configured OAuthToolkit.

  Args:
      configured_oauth_toolkit: Fixture providing configured OAuthToolkit

  Returns:
      str: Encoded JWT token
  """
  return configured_oauth_toolkit.token
