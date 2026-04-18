"""
Example: Send SMS using the asynchronous AsyncKiboNetClient.
"""

import asyncio
import os

from kibonet_sdk import AsyncKiboNetClient
from kibonet_sdk.exceptions import KiboNetError

API_KEY = os.environ.get("KIBONET_API_KEY", "YOUR_API_KEY")
API_SECRET = os.environ.get("KIBONET_API_SECRET", "YOUR_API_SECRET")


async def main():
    async with AsyncKiboNetClient(api_key=API_KEY, api_secret=API_SECRET) as client:
        if not await client.is_healthy():
            print("KiboNet API is not reachable.")
            return

        try:
            response = await client.send_sms(
                sender_id="MyBrand",
                message="Hello from async KiboNet SDK!",
                contacts=["255712345678"],
                delivery_report_url="https://myserver.com/delivery-callback",
            )
            print(f"Shoot ID: {response['data']['shootId']}")
            print(f"Valid contacts: {response['data']['validContacts']}")

        except KiboNetError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
