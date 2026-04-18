"""
Example: Retrieve delivery report for a sent message.
"""

import os
from kibonet_sdk import KiboNetClient
from kibonet_sdk.exceptions import KiboNetError

API_KEY = os.environ.get("KIBONET_API_KEY", "YOUR_API_KEY")
API_SECRET = os.environ.get("KIBONET_API_SECRET", "YOUR_API_SECRET")
SHOOT_ID = os.environ.get("KIBONET_SHOOT_ID", "YOUR_SHOOT_ID")

with KiboNetClient(api_key=API_KEY, api_secret=API_SECRET) as client:
    try:
        result = client.get_delivery_report(SHOOT_ID)
        print(f"Report message: {result['message']}")
        for record in result["data"]:
            print(
                f"  Mobile : {record['mobile']}"
                f"  Status : {record['status']} ({record['statusCode']})"
                f"  Sent at: {record['sentAt']}"
            )
    except KiboNetError as e:
        print(f"Error: {e}")
