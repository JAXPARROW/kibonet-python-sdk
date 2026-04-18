# KiboNet Python SDK

Simple, secure Python SDK for the [KiboNet SMS Gateway](https://sms.kibonet.co.tz).  
Supports both **synchronous** and **async** usage via [httpx](https://www.python-httpx.org/).

[![PyPI version](https://img.shields.io/pypi/v/kibonet-python-sdk)](https://pypi.org/project/kibonet-python-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/kibonet-python-sdk)](https://pypi.org/project/kibonet-python-sdk/)
[![License: MIT](https://img.shields.io/pypi/l/kibonet-python-sdk)](https://pypi.org/project/kibonet-python-sdk/)

## Features

- **Send SMS** to one or multiple recipients (comma-separated contacts)
- **Delivery reports** retrieved by `shootId`
- **Balance check** for your SMS credits
- **Health check** — `is_healthy()` never raises, perfect for monitoring probes
- **Async support** — full `async`/`await` via `AsyncKiboNetClient`
- **httpx** under the hood — connection pooling, automatic retries, TLS verification
- **Phone number validation** — auto-converts `0XXXXXXXXX` → `255XXXXXXXXX`
- **Typed exceptions** — catch exactly what you need
- **Context manager** support (both sync and async)
- **No credentials in code** — load from environment variables

## Installation

```bash
pip install kibonet-python-sdk
```

## Quick Start

### Synchronous

```python
from kibonet_sdk import KiboNetClient

with KiboNetClient(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET") as client:
    # Health check
    if client.is_healthy():
        print("API is up!")

    # Send SMS
    resp = client.send_sms(
        sender_id="MyBrand",
        message="Hello from KiboNet!",
        contacts=["255712345678", "255798765432"],
        delivery_report_url="https://myserver.com/delivery-callback",  # optional
    )
    print(f"Shoot ID: {resp['data']['shootId']}")
    print(f"Valid: {resp['data']['validContacts']}")
```

### Asynchronous

```python
import asyncio
from kibonet_sdk import AsyncKiboNetClient

async def main():
    async with AsyncKiboNetClient(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET") as client:
        if await client.is_healthy():
            resp = await client.send_sms(
                sender_id="MyBrand",
                message="Hello async!",
                contacts="255712345678",
            )
            print(resp["data"]["shootId"])

asyncio.run(main())
```

## All Methods

Both `KiboNetClient` and `AsyncKiboNetClient` expose the same interface:

### `send_sms`

```python
resp = client.send_sms(
    sender_id="MyBrand",        # Sender name shown to recipient
    message="Your OTP is 1234", # SMS text
    contacts=[                  # Single string, list, or CSV string
        "255712345678",
        "255798765432",
    ],
    delivery_report_url="https://myserver.com/callback",  # optional
    message_type="text",        # currently only "text" is supported
)

# Response
print(resp["data"]["shootId"])          # Use this for delivery reports
print(resp["data"]["validContacts"])    # int
print(resp["data"]["invalidContacts"])  # int
print(resp["data"]["duplicatedContacts"])
print(resp["data"]["messageSize"])      # character count
```

### `get_delivery_report`

```python
report = client.get_delivery_report("abcd1234-5678-efgh-9012-ijklmnopqrst")

for record in report["data"]:
    print(record["mobile"])      # 255712345678
    print(record["status"])      # Delivered / Failed / Buffered
    print(record["statusCode"])  # 000
    print(record["sentAt"])      # "07-02-2024 07:35:08"
```

### `get_balance`

```python
result = client.get_balance()
print(result["data"]["totalSms"])  # e.g. 30
```

### `is_healthy`

```python
if client.is_healthy():
    print("API is reachable and credentials are valid")
```

## Phone Number Formats

The SDK automatically normalises phone numbers:

| Input format       | Stored as      |
|--------------------|----------------|
| `0712345678`       | `255712345678` |
| `+255712345678`    | `255712345678` |
| `255712345678`     | `255712345678` |

## Error Handling

```python
from kibonet_sdk import KiboNetClient
from kibonet_sdk.exceptions import (
    KiboNetAuthenticationError,
    KiboNetValidationError,
    KiboNetRateLimitError,
    KiboNetInsufficientBalanceError,
    KiboNetConnectionError,
    KiboNetServerError,
    KiboNetAPIError,
    KiboNetError,        # base — catch everything SDK-related
)

client = KiboNetClient(api_key="...", api_secret="...")

try:
    client.send_sms(sender_id="X", message="Hi", contacts="255712345678")
except KiboNetAuthenticationError:
    print("Bad credentials")
except KiboNetValidationError as e:
    print(f"Input error: {e}")
except KiboNetRateLimitError:
    print("Slow down — rate limited")
except KiboNetConnectionError as e:
    print(f"Network error: {e}")
except KiboNetServerError as e:
    print(f"KiboNet server problem: {e}")
except KiboNetAPIError as e:
    print(f"API error (code={e.code}): {e}")
```

## Environment Variables

Keep credentials out of source code:

```bash
export KIBONET_API_KEY="your_api_key"
export KIBONET_API_SECRET="your_api_secret"
```

```python
import os
from kibonet_sdk import KiboNetClient

client = KiboNetClient(
    api_key=os.environ["KIBONET_API_KEY"],
    api_secret=os.environ["KIBONET_API_SECRET"],
)
```

## Constructor Options

```python
KiboNetClient(
    api_key: str,          # Required — from KiboNet portal
    api_secret: str,       # Required — from KiboNet portal
    timeout: float = 30.0, # Per-request timeout in seconds
    max_retries: int = 3,  # Automatic retries on transient failures
    logger=None,           # Optional logging.Logger
)
```

`AsyncKiboNetClient` takes the same parameters.

## Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = KiboNetClient(api_key="...", api_secret="...")
# All HTTP calls are logged at DEBUG level
```

## Development

```bash
git clone https://github.com/JAXPARROW/kibonet-python-sdk.git
cd kibonet-python-sdk
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=kibonet_sdk --cov-report=term-missing

# Build
python -m build
```

## License

MIT — see [LICENSE](LICENSE).

## Contributors

- **Jackson Linus** — Creator and maintainer
