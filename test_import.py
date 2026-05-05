#!/usr/bin/env python3
"""Test script to verify oatk can be imported."""
import sys

try:
    import oatk
    print("SUCCESS: oatk imported successfully")
    print(f"oatk version: {oatk.__version__}")
    sys.exit(0)
except ImportError as e:
    print(f"FAILED: Could not import oatk: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Unexpected error importing oatk: {e}")
    sys.exit(1)