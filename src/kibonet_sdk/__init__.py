"""
KiboNet Python SDK — simple, secure SMS gateway client for Python.

Quickstart (sync)::

    from kibonet_sdk import KiboNetClient

    with KiboNetClient(api_key="YOUR_KEY", api_secret="YOUR_SECRET") as client:
        resp = client.send_sms(
            sender_id="MyBrand",
            message="Hello from KiboNet!",
            contacts=["255712345678"],
        )
        print(resp["data"]["shootId"])

Quickstart (async)::

    import asyncio
    from kibonet_sdk import AsyncKiboNetClient

    async def main():
        async with AsyncKiboNetClient(api_key="YOUR_KEY", api_secret="YOUR_SECRET") as client:
            resp = await client.send_sms(
                sender_id="MyBrand",
                message="Hello async!",
                contacts=["255712345678"],
            )
            print(resp["data"]["shootId"])

    asyncio.run(main())
"""

from .client import KiboNetClient
from .async_client import AsyncKiboNetClient
from .exceptions import (
    KiboNetError,
    KiboNetAuthenticationError,
    KiboNetValidationError,
    KiboNetAPIError,
    KiboNetRateLimitError,
    KiboNetInsufficientBalanceError,
    KiboNetConnectionError,
    KiboNetServerError,
)

__all__ = [
    # Clients
    "KiboNetClient",
    "AsyncKiboNetClient",
    # Exceptions
    "KiboNetError",
    "KiboNetAuthenticationError",
    "KiboNetValidationError",
    "KiboNetAPIError",
    "KiboNetRateLimitError",
    "KiboNetInsufficientBalanceError",
    "KiboNetConnectionError",
    "KiboNetServerError",
]

__version__ = "0.1.1"
