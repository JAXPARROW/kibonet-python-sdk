"""
Example: Send SMS using the synchronous KiboNetClient.
"""

import os
from kibonet_sdk import KiboNetClient
from kibonet_sdk.exceptions import KiboNetError

API_KEY = os.environ.get("KIBONET_API_KEY", "YOUR_API_KEY")
API_SECRET = os.environ.get("KIBONET_API_SECRET", "YOUR_API_SECRET")

with KiboNetClient(api_key=API_KEY, api_secret=API_SECRET) as client:
    # Health check first
    if not client.is_healthy():
        print("KiboNet API is not reachable. Check credentials and connectivity.")
        raise SystemExit(1)

    try:
        response = client.send_sms(
            sender_id="MyBrand",
            message="Hello from KiboNet Python SDK!",
            contacts=["255712345678", "255798765432"],
            delivery_report_url="https://myserver.com/delivery-callback",
        )
        data = response["data"]
        print(f"Message submitted successfully!")
        print(f"  Shoot ID     : {data['shootId']}")
        print(f"  Valid        : {data['validContacts']}")
        print(f"  Invalid      : {data['invalidContacts']}")
        print(f"  Duplicated   : {data['duplicatedContacts']}")
        print(f"  Message size : {data['messageSize']} chars")

    except KiboNetError as e:
        print(f"Error: {e}")
