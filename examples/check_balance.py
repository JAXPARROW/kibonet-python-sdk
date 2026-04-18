"""
Example: Check SMS credit balance.
"""

import os
from kibonet_sdk import KiboNetClient
from kibonet_sdk.exceptions import KiboNetError

API_KEY = os.environ.get("KIBONET_API_KEY", "YOUR_API_KEY")
API_SECRET = os.environ.get("KIBONET_API_SECRET", "YOUR_API_SECRET")

with KiboNetClient(api_key=API_KEY, api_secret=API_SECRET) as client:
    try:
        result = client.get_balance()
        print(f"SMS balance: {result['data']['totalSms']} messages")
    except KiboNetError as e:
        print(f"Error: {e}")
