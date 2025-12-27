#!/usr/bin/env python3
"""Test environment variable loading"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get ALLOWED_ORIGINS
origins_str = os.getenv("ALLOWED_ORIGINS", "NOT_FOUND")
print(f"Raw ALLOWED_ORIGINS: '{origins_str}'")

# Parse it
if origins_str != "NOT_FOUND":
    origins_list = [origin.strip() for origin in origins_str.split(",")]
    print(f"Parsed origins list: {origins_list}")

    # Check each
    for i, origin in enumerate(origins_list):
        print(f"  [{i}] '{origin}' (len={len(origin)})")
