"""
Async HTTP client abstraction for OAuth operations.

This module provides async HTTP client support using httpx, while maintaining
backward compatibility with the synchronous requests-based operations.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class AsyncHttpClient:
  """
  Async HTTP client wrapper for OAuth operations.

  This class provides an async interface for HTTP operations using httpx.
  It's designed to be used as an async context manager for proper resource
  management.

  Example:
      async with AsyncHttpClient() as client:
          response = await client.get("https://example.com/.well-known/openid-configuration")
          config = response.json()

  Attributes:
      _client: The underlying httpx.AsyncClient instance
      _timeout: Default timeout for requests in seconds
  """

  def __init__(self, timeout: float = 30.0) -> None:
    """
    Initialize the async HTTP client.

    Args:
        timeout: Default timeout for HTTP requests in seconds
    """
    self._client: httpx.AsyncClient | None = None
    self._timeout = timeout

  async def __aenter__(self) -> AsyncHttpClient:
    """
    Enter async context manager and create the HTTP client.

    Returns:
        The AsyncHttpClient instance
    """
    self._client = httpx.AsyncClient(timeout=self._timeout)
    return self

  async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
    """
    Exit async context manager and close the HTTP client.

    Args:
        exc_type: Exception type if an exception was raised
        exc_val: Exception value if an exception was raised
        exc_tb: Exception traceback if an exception was raised
    """
    if self._client is not None:
      await self._client.aclose()
    self._client = None

  async def get(
    self,
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
  ) -> httpx.Response:
    """
    Perform an async HTTP GET request.

    Args:
        url: The URL to request
        params: Optional query parameters
        headers: Optional request headers

    Returns:
        The HTTP response

    Raises:
        RuntimeError: If client is not initialized (not used as context manager)
        httpx.HTTPError: If the request fails
    """
    if self._client is None:
      raise RuntimeError("AsyncHttpClient must be used as an async context manager")

    logger.debug(f"GET {url}")
    response = await self._client.get(url, params=params, headers=headers)
    logger.debug(f"GET {url} -> {response.status_code}")
    return response

  async def post(
    self,
    url: str,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
  ) -> httpx.Response:
    """
    Perform an async HTTP POST request.

    Args:
        url: The URL to request
        data: Optional form data
        json: Optional JSON body
        headers: Optional request headers

    Returns:
        The HTTP response

    Raises:
        RuntimeError: If client is not initialized (not used as context manager)
        httpx.HTTPError: If the request fails
    """
    if self._client is None:
      raise RuntimeError("AsyncHttpClient must be used as an async context manager")

    logger.debug(f"POST {url}")
    response = await self._client.post(url, data=data, json=json, headers=headers)
    logger.debug(f"POST {url} -> {response.status_code}")
    return response

  @property
  def is_connected(self) -> bool:
    """
    Check if the client is connected and ready to make requests.

    Returns:
        True if the client is initialized, False otherwise
    """
    return self._client is not None
