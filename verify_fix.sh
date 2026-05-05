#!/bin/bash
# Verification script to test dependency fix

set -e  # Exit on error

echo "=== Running uv sync to install dependencies ==="
uv sync

echo ""
echo "=== Verifying oatk import ==="
uv run python test_import.py

echo ""
echo "=== Verification complete ==="