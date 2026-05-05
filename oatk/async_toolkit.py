"""
Async OAuthToolkit implementation.

This module provides an async version of OAuthToolkit that uses async operations
for HTTP and file I/O while maintaining the same fluent API pattern.
"""

import json
import logging
import uuid
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

import anyio
import jwt

from oatk import fake
from oatk.async_client import AsyncHttpClient
from oatk.types import ClaimsDict, Decorator, JWKSDict, RequiredClaims

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
  from AppKit import NSPasteboard

try:
  from AppKit import NSPasteboard, NSStringPboardType

  pb: Optional["NSPasteboard"] = NSPasteboard.generalPasteboard()
except ModuleNotFoundError:
  logger.debug("No AppKit installed, so no MacOS clipboard support!")
  pb = None


class AsyncOAuthToolkit:
  """
  Async version of OAuthToolkit for use with async frameworks.

  This class mirrors the synchronous OAuthToolkit API but uses async operations
  for HTTP and file I/O. The fluent API pattern (method chaining) is maintained.

  Key differences from sync version:
  - `using_provider()` and `init_from_provider()` are async
  - `with_jwks()` has async file I/O when reading from file paths
  - `validate()` can optionally use run_in_executor for CPU-bound operations
  - HTTP operations use AsyncHttpClient instead of requests

  Example:
      async with AsyncOAuthToolkit() as toolkit:
          await toolkit.using_provider("https://example.com/.well-known/openid-configuration")
          claims = await toolkit.validate(token)

  Attributes:
      _encoded: The encoded JWT token (if loaded)
      _provider_url: The OAuth provider URL
      _certs: Dictionary of kid -> RSAPublicKey for validation
      _private_key: RSA private key for token generation
      _public_key: RSA public key for validation
      _alg: Algorithm (default RS256)
      _kid: Key ID for the current key
      _claims: Claims for token generation
      _client_id: OAuth client ID for audience validation
      server: Fake OAuth server instance
  """

  def __init__(self) -> None:
    """Initialize an AsyncOAuthToolkit instance with default values."""
    self._encoded: Optional[str] = None
    self._provider_url: Optional[str] = None
    self._certs: Dict[str, Any] = {}
    self._private_key: Optional[Any] = None
    self._public_key: Optional[Any] = None
    self._alg: str = "RS256"
    self._kid: str = str(uuid.uuid4())
    self._claims: ClaimsDict = {}
    self._client_id: Optional[str] = None

    self.server = fake.server
    self.server.oatk = self

  def _log_certs(self, msg: str) -> None:
    """
    Log certificate information for debugging.

    Args:
        msg: Message to log
    """
    logger.info(msg)
    logger.info(json.dumps(list(self._certs.keys()), indent=2, default=str))

  async def with_private(self, path: str) -> "AsyncOAuthToolkit":
    """
    Load a private key from a PEM file asynchronously.

    Args:
        path: Path to the private key PEM file

    Returns:
        Self for method chaining

    Note:
        This method uses async file I/O via anyio for better performance
        in async contexts.
    """
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    async with await anyio.open_file(path, "rb") as fp:
      key_data = await fp.read()

    self._private_key = serialization.load_pem_private_key(
      key_data, password=None, backend=default_backend()
    )
    return self

  async def with_public(self, path: str) -> "AsyncOAuthToolkit":
    """
    Load a public key from a PEM file asynchronously.

    Args:
        path: Path to the public key PEM file

    Returns:
        Self for method chaining
    """
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    async with await anyio.open_file(path, "rb") as fp:
      key_data = await fp.read()

    self._public_key = serialization.load_pem_public_key(
      key_data, backend=default_backend()
    )
    self._certs = {self._kid: self._public_key}
    self._log_certs("certs set from path to")
    return self

  async def using_provider(self, provider_url: str) -> Optional["AsyncOAuthToolkit"]:
    """
    Configure the toolkit from an OAuth provider's discovery endpoint.

    This method sets the provider URL and then calls init_from_provider()
    to fetch the configuration and JWKS.

    Args:
        provider_url: The OAuth provider's discovery URL
                      (typically /.well-known/openid-configuration)

    Returns:
        Self for method chaining, or None if initialization fails

    Example:
        toolkit = await AsyncOAuthToolkit().using_provider(
            "https://accounts.google.com/.well-known/openid-configuration"
        )
    """
    self._provider_url = provider_url
    return await self.init_from_provider()

  async def init_from_provider(self) -> Optional["AsyncOAuthToolkit"]:
    """
    Initialize the toolkit from the configured provider URL.

    Fetches the OpenID configuration and JWKS from the provider.
    This is an async version that uses AsyncHttpClient.

    Returns:
        Self for method chaining, or None if initialization fails

    Raises:
        ValueError: If provider_url is not set

    Note:
        This method must be called after using_provider() or with
        a pre-configured _provider_url.
    """
    if not self._provider_url:
      raise ValueError("missing provider url, use `using_provider` to supply")

    try:
      async with AsyncHttpClient() as client:
        # Fetch OpenID configuration
        response = await client.get(self._provider_url)
        config = response.json()

        # Fetch JWKS
        jwks_response = await client.get(config["jwks_uri"])
        jwks_data = jwks_response.content

        await self.with_jwks(jwks_data)
    except Exception:
      logger.exception("could not initialize from provider")
      return None

    logger.info(f"successfully configured from {self._provider_url}")
    return self

  def with_client_id(self, client_id: str) -> "AsyncOAuthToolkit":
    """
    Set the OAuth client ID for audience validation.

    Args:
        client_id: The OAuth client ID

    Returns:
        Self for method chaining
    """
    self._client_id = client_id
    return self

  @property
  def jwks(self) -> str:
    """
    Get the JWKS representation of the current public key.

    Returns:
        JSON string containing JWKS with one key
    """
    from authlib.jose import jwk

    return json.dumps(
      {
        "keys": [
          jwk.dumps(self._public_key, kty="RSA", alg=self._alg, kid=self._kid)
        ]
      },
      indent=2,
    )

  async def with_jwks(
    self, path_or_string_or_obj: Union[str, bytes, JWKSDict]
  ) -> "AsyncOAuthToolkit":
    """
    Load JWKS from a file path, JSON string, or dictionary.

    This method handles three input types:
    1. File path (str): Load JWKS from file (async I/O)
    2. JSON string/bytes: Parse JSON to get JWKS dict
    3. JWKS dictionary: Use directly

    Args:
        path_or_string_or_obj: Path to JWKS file, JSON string/bytes, or JWKS dict

    Returns:
        Self for method chaining

    Note:
        For file paths, this method uses async file I/O via anyio.
        For strings and bytes, parsing is synchronous (CPU-bound).
    """
    try:
      # Try to open as a file path (async)
      async with await anyio.open_file(path_or_string_or_obj) as fp:
        jwks: JWKSDict = json.loads(await fp.read())
    except Exception:
      # If file open fails, try to parse as JSON string/bytes
      try:
        jwks = json.loads(path_or_string_or_obj)
      except Exception:
        # If that fails, assume it's already a JWKS dict
        jwks = path_or_string_or_obj  # type: ignore

    assert isinstance(jwks, dict)
    self._certs = {
      key["kid"]: jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
      for key in jwks["keys"]
    }
    self._log_certs("certs set from jwks to")

    if jwks["keys"]:
      self._kid = jwks["keys"][0]["kid"]
    return self

  def from_clipboard(self) -> "AsyncOAuthToolkit":
    """
    Load a token from the system clipboard (macOS only).

    Returns:
        Self for method chaining

    Raises:
        RuntimeError: If clipboard is not available (not macOS)

    Note:
        This method is synchronous because it only reads from memory.
    """
    if pb is None:
      raise RuntimeError("Clipboard not available on this platform")

    encoded = pb.stringForType_(NSStringPboardType)
    if encoded[:6] == "Bearer":
      encoded = encoded[7:]

    self._encoded = encoded.strip()  # strip to remove trailing newline
    return self

  async def from_file(self, path: str) -> "AsyncOAuthToolkit":
    """
    Load a token from a file asynchronously.

    Args:
        path: Path to file containing the token

    Returns:
        Self for method chaining
    """
    async with await anyio.open_file(path) as fp:
      self._encoded = (await fp.read()).strip()  # strip to remove trailing newline
    return self

  def header(self, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the header of a JWT token without validating it.

    Args:
        token: The JWT token, or None to use the loaded token

    Returns:
        Dictionary containing the JWT header

    Note:
        This method is synchronous (CPU-bound operation).
    """
    if not token:
      token = self._encoded
    return jwt.get_unverified_header(token)

  def claims(
    self, claimsdict: Optional[ClaimsDict] = None, **claimset: Any
  ) -> "AsyncOAuthToolkit":
    """
    Set claims for token generation.

    Args:
        claimsdict: Optional dictionary of claims
        **claimset: Additional claims as keyword arguments

    Returns:
        Self for method chaining
    """
    if claimsdict is None:
      claimsdict = {}
    self._claims = claimset
    self._claims.update(claimsdict)
    return self

  @property
  def token(self) -> Optional[str]:
    """
    Generate a JWT token from the configured private key and claims.

    Returns:
        Encoded JWT token, or None if no private key is configured

    Note:
        This property is synchronous because token generation is CPU-bound.
    """
    if self._private_key:
      return jwt.encode(
        self._claims,
        self._private_key,
        algorithm=self._alg,
        headers={"kid": self._kid, "alg": self._alg},
      )
    return None

  async def validate(self, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate a JWT token asynchronously.

    This method validates the token signature and claims. If the token's
    key ID (kid) is not found in the cached certificates, it will attempt
    to refresh from the provider.

    Args:
        token: The JWT token to validate, or None to use the loaded token

    Returns:
        Dictionary containing the validated claims

    Raises:
        KeyError: If the token's key ID is not found in certificates
        jwt.InvalidTokenError: If the token is invalid

    Note:
        This method uses run_in_executor for CPU-bound JWT validation
        to avoid blocking the async event loop.
    """
    kid = self.header(token)["kid"]
    alg = self.header(token)["alg"]

    if not token:
      token = self._encoded

    try:
      cert = self._certs[kid]
    except KeyError:
      self._log_certs(f"unknown cert? {kid}")
      logger.error("retrying provider initialization")
      _ = await self.init_from_provider()
      try:
        cert = self._certs[kid]
      except KeyError:
        self._log_certs(f"retry failed, still unknown cert? {kid}")
        raise

    # Use anyio to run CPU-bound JWT validation in a thread pool
    # This prevents blocking the async event loop
    return await anyio.to_thread.run_sync(
      lambda: jwt.decode(token, cert, algorithms=[alg], audience=self._client_id)
    )

  def decode(self, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Decode a JWT token without validating the signature.

    Args:
        token: The JWT token to decode, or None to use the loaded token

    Returns:
        Dictionary containing the decoded claims

    Note:
        This method is synchronous (CPU-bound operation).
        WARNING: This does NOT validate the token signature!
    """
    if not token:
      token = self._encoded
    return jwt.decode(token, options={"verify_signature": False})

  async def execute_authenticated(
    self,
    f: Callable[..., Any],
    required_claims: Optional[RequiredClaims] = None,
    *args: Any,
    **kwargs: Any,
  ) -> Any:
    """
    Execute a function after authenticating a request.

    This is designed for use with async web frameworks (Quart, FastAPI, etc.)
    that provide request context.

    Args:
        f: The function to execute after authentication
        required_claims: Optional dictionary of required claims
        *args: Positional arguments to pass to f
        **kwargs: Keyword arguments to pass to f

    Returns:
        The result of f(*args, **kwargs) if authenticated, or an error response

    Note:
        This method requires request context from an async framework.
        Implementation is framework-specific.
    """
    # Note: This implementation requires framework-specific request context
    # For Quart/FastAPI, you would access request.headers differently
    # This is a placeholder that should be overridden in framework-specific subclasses
    raise NotImplementedError(
      "execute_authenticated requires framework-specific implementation. "
      "Use framework-specific decorators (e.g., authenticated_async)."
    )

  def authenticated(self, f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for authenticating async routes.

    This decorator validates the Authorization header and executes the
    decorated function only if authentication succeeds.

    Args:
        f: The async function to decorate

    Returns:
        Decorated function that validates authentication

    Note:
        This is a placeholder for framework-specific decorators.
        Use framework-specific versions (e.g., quart_authenticated).
    """
    @wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
      return await self.execute_authenticated(f, None, *args, **kwargs)

    return wrapper

  def authenticated_with_claims(
    self, **required_claims: Union[str, Callable[[Any], bool]]
  ) -> Decorator:
    """
    Decorator factory for authenticating async routes with required claims.

    Args:
        **required_claims: Required claims as keyword arguments

    Returns:
        Decorator function

    Note:
        This is a placeholder for framework-specific decorators.
        Use framework-specific versions.
    """
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
      @wraps(f)
      async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await self.execute_authenticated(f, required_claims, *args, **kwargs)

      return wrapper

    return decorator