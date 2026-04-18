"""
Example: Liveness / readiness health check.
"""

import os
from kibonet_sdk import KiboNetClient

API_KEY = os.environ.get("KIBONET_API_KEY", "YOUR_API_KEY")
API_SECRET = os.environ.get("KIBONET_API_SECRET", "YOUR_API_SECRET")

client = KiboNetClient(api_key=API_KEY, api_secret=API_SECRET)

if client.is_healthy():
    print("KiboNet API is healthy and credentials are valid.")
else:
    print("KiboNet API is unreachable or credentials are invalid.")

client.close()
