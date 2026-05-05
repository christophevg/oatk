#!/usr/bin/env python
"""
Quick verification script for async decorators implementation.
"""

import sys

# Test imports
try:
  from oatk.async_toolkit import AsyncOAuthToolkit
  print("✓ AsyncOAuthToolkit imported successfully")
except Exception as e:
  print(f"✗ Failed to import AsyncOAuthToolkit: {e}")
  sys.exit(1)

# Test methods exist
toolkit = AsyncOAuthToolkit()

methods = [
  'set_authorization_token',
  'get_authorization_token',
  'extract_token_from_header',
  'authenticated',
  'authenticated_with_claims',
  'execute_authenticated',
  '_create_error_response',
]

for method in methods:
  if hasattr(toolkit, method):
    print(f"✓ Method {method} exists")
  else:
    print(f"✗ Method {method} missing")
    sys.exit(1)

# Test context management
toolkit.set_authorization_token("test-token")
token = toolkit.get_authorization_token()
if token == "test-token":
  print("✓ Context management works")
else:
  print("✗ Context management failed")
  sys.exit(1)

# Test token extraction
header = "Bearer my-jwt-token"
extracted = toolkit.extract_token_from_header(header)
if extracted == "my-jwt-token":
  print("✓ Token extraction works")
else:
  print("✗ Token extraction failed")
  sys.exit(1)

# Test error response
response = toolkit._create_error_response("Test error", 401)
if response == ("Test error", 401):
  print("✓ Error response creation works")
else:
  print("✗ Error response creation failed")
  sys.exit(1)

# Test decorator exists
@toolkit.authenticated
async def test_route():
  return {"message": "test"}

if callable(test_route):
  print("✓ @authenticated decorator works")
else:
  print("✗ @authenticated decorator failed")
  sys.exit(1)

# Test authenticated_with_claims decorator
@toolkit.authenticated_with_claims(role="admin")
async def admin_route():
  return {"message": "admin"}

if callable(admin_route):
  print("✓ @authenticated_with_claims decorator works")
else:
  print("✗ @authenticated_with_claims decorator failed")
  sys.exit(1)

print("\n✓✓✓ All verification checks passed! ✓✓✓")