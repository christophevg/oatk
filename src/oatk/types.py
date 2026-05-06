"""Type definitions for oatk."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeAlias

# JWT claims type
ClaimsDict: TypeAlias = dict[str, Any]

# JWKS type
JWKSDict: TypeAlias = dict[str, Any]

# Decorator types
Decorator: TypeAlias = Callable[..., Callable[..., Any]]

# Claims validation types
ClaimValue: TypeAlias = str | list[str] | Callable[[Any], bool]
RequiredClaims: TypeAlias = dict[str, ClaimValue]
