"""
Shared pytest fixtures for the KiboNet SDK test suite.
"""

import sys
import os

import pytest
import respx
import httpx

# Make sure the local src package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from kibonet_sdk import KiboNetClient, AsyncKiboNetClient  # noqa: E402

BASE_URL = "https://sms.kibonet.co.tz"


# ---------------------------------------------------------------------------
# Client fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Synchronous KiboNetClient with dummy credentials."""
    return KiboNetClient(api_key="test_key", api_secret="test_secret")


@pytest.fixture
async def async_client():
    """Asynchronous KiboNetClient with dummy credentials."""
    c = AsyncKiboNetClient(api_key="test_key", api_secret="test_secret")
    yield c
    await c.aclose()


# ---------------------------------------------------------------------------
# Sample API response fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def send_sms_response():
    return {
        "code": 200,
        "data": {
            "validContacts": 2,
            "invalidContacts": 0,
            "duplicatedContacts": 0,
            "messageSize": 20,
            "message": "Hello KiboNet!",
            "shootId": "abcd1234-5678-efgh-9012-ijklmnopqrst",
        },
        "success": True,
        "message": "Message submit",
    }


@pytest.fixture
def delivery_report_response():
    return {
        "code": 200,
        "data": [
            {
                "message": "Hello KiboNet!",
                "mobile": "255712345678",
                "senderId": "MyBrand",
                "status": "Delivered",
                "statusCode": "000",
                "explanation": "N/A",
                "messageType": "text",
                "sentAt": "07-02-2024 07:35:08",
            }
        ],
        "success": True,
        "message": "Sent messages report",
    }


@pytest.fixture
def balance_response():
    return {
        "code": 200,
        "data": {"totalSms": 30},
        "success": True,
        "message": "Balance",
    }
