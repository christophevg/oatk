"""Type definitions for oatk."""

from typing import Any, Callable, Dict, List, Optional, Union

# JWT claims type
ClaimsDict = Dict[str, Any]

# JWKS type
JWKSDict = Dict[str, Any]

# Decorator types
Decorator = Callable[..., Callable[..., Any]]

# Claims validation types
ClaimValue = Union[str, List[str], Callable[[Any], bool]]
RequiredClaims = Dict[str, ClaimValue]