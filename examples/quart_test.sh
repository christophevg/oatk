#!/bin/bash
# Test script for Quart OAuth example
# This script starts the server and runs curl commands against it

set -e

echo "========================================"
echo "Quart OAuth Example - Live Testing"
echo "========================================"
echo ""

# Start server in background
echo "- Starting Quart server..."
uv run uvicorn examples.quart_example:app --port 8000 > /tmp/quart-server.log 2>&1 &
SERVER_PID=$!
echo "  Server started (PID: $SERVER_PID)"

# Wait for server to be ready
echo "  Waiting for server to initialize..."
for i in {1..30}; do
  if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "  Server is ready!"
    break
  fi
  sleep 0.5
done

echo ""
echo "- Testing public endpoint (no auth required)..."
echo "  curl http://localhost:8000/"
RESPONSE=$(curl -s http://localhost:8000/)
echo "  Response: $RESPONSE"
echo ""

echo "- Testing protected endpoint without token (should fail)..."
echo "  curl http://localhost:8000/protected"
RESPONSE=$(curl -s http://localhost:8000/protected)
echo "  Response: $RESPONSE"
echo ""

# Generate a test token using the project's test keys
echo "- Generating test token..."
TOKEN=$(uv run python -c "
import sys
sys.path.insert(0, 'src')
from oatk import OAuthToolkit
import time

# Create toolkit with the same keys as the server
toolkit = OAuthToolkit()
toolkit.with_private('private_key.pem')
toolkit.with_public('public_key.pem')
toolkit.with_jwks('certs.json')

# Generate token
toolkit.claims(
    sub='test-user',
    role='admin',
    exp=int(time.time()) + 3600
)
print(toolkit.token)
" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo "  Token generated successfully"
    echo ""

    echo "- Testing protected endpoint with valid token..."
    echo "  curl -H 'Authorization: Bearer <token>' http://localhost:8000/protected"
    RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/protected)
    echo "  Response: $RESPONSE"
    echo ""

    echo "- Testing admin endpoint with admin token..."
    echo "  curl -H 'Authorization: Bearer <admin-token>' http://localhost:8000/admin"
    RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin)
    echo "  Response: $RESPONSE"
    echo ""

    echo "- Testing user endpoint with matching user..."
    # Generate token for specific user
    TOKEN2=$(uv run python -c "
import sys
sys.path.insert(0, 'src')
from oatk import OAuthToolkit
import time

# Create toolkit with the same keys as the server
toolkit = OAuthToolkit()
toolkit.with_private('private_key.pem')
toolkit.with_public('public_key.pem')
toolkit.with_jwks('certs.json')

toolkit.claims(
    sub='test-user-123',
    role='user',
    exp=int(time.time()) + 3600
)
print(toolkit.token)
" 2>/dev/null)

    echo "  curl -H 'Authorization: Bearer <user-token>' http://localhost:8000/user"
    RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN2" http://localhost:8000/user)
    echo "  Response: $RESPONSE"
    echo ""
else
    echo "  Warning: Could not generate test token"
fi

echo "- Stopping server..."
kill $SERVER_PID 2>/dev/null || true
echo "  Server stopped"
echo ""
echo "========================================"
