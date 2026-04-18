"""
Tests for the asynchronous AsyncKiboNetClient.
"""

import pytest
import respx
import httpx

from kibonet_sdk import AsyncKiboNetClient
from kibonet_sdk.exceptions import (
    KiboNetAuthenticationError,
    KiboNetAPIError,
    KiboNetRateLimitError,
    KiboNetServerError,
    KiboNetValidationError,
)

BASE_URL = "https://sms.kibonet.co.tz"


class TestAsyncKiboNetClientInit:

    def test_rejects_empty_api_key(self):
        with pytest.raises(KiboNetValidationError):
            AsyncKiboNetClient(api_key="", api_secret="secret")

    def test_rejects_empty_api_secret(self):
        with pytest.raises(KiboNetValidationError):
            AsyncKiboNetClient(api_key="key", api_secret="")

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        async with AsyncKiboNetClient(api_key="k", api_secret="s") as c:
            assert c is not None


class TestAsyncIsHealthy:

    @pytest.mark.asyncio
    @respx.mock
    async def test_healthy_returns_true(self, balance_response):
        respx.get(f"{BASE_URL}/api/v1/vendor/message/balance").mock(
            return_value=httpx.Response(200, json=balance_response)
        )
        async with AsyncKiboNetClient(api_key="k", api_secret="s") as c:
            assert await c.is_healthy() is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_unhealthy_returns_false(self):
        respx.get(f"{BASE_URL}/api/v1/vendor/message/balance").mock(
            return_value=httpx.Response(401)
        )
        async with AsyncKiboNetClient(api_key="k", api_secret="s") as c:
            assert await c.is_healthy() is False


class TestAsyncSendSMS:

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_sms_single_recipient(self, async_client, send_sms_response):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(200, json=send_sms_response)
        )
        result = await async_client.send_sms(
            sender_id="TestSender",
            message="Hello async KiboNet!",
            contacts="255712345678",
        )
        assert result["success"] is True
        assert result["data"]["shootId"] == "abcd1234-5678-efgh-9012-ijklmnopqrst"

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_sms_multiple_recipients(self, async_client, send_sms_response):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(200, json=send_sms_response)
        )
        result = await async_client.send_sms(
            sender_id="TestSender",
            message="Async bulk message",
            contacts=["255712345678", "255798765432"],
        )
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_send_sms_empty_sender_raises(self, async_client):
        with pytest.raises(KiboNetValidationError):
            await async_client.send_sms(
                sender_id="", message="Hi", contacts="255712345678"
            )

    @pytest.mark.asyncio
    async def test_send_sms_empty_message_raises(self, async_client):
        with pytest.raises(KiboNetValidationError):
            await async_client.send_sms(
                sender_id="Sender", message="", contacts="255712345678"
            )

    @pytest.mark.asyncio
    async def test_send_sms_invalid_phone_raises(self, async_client):
        with pytest.raises(ValueError):
            await async_client.send_sms(
                sender_id="Sender", message="Hi", contacts="bad_number"
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_sms_auth_error(self, async_client):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(401, json={"error": "unauthorised"})
        )
        with pytest.raises(KiboNetAuthenticationError):
            await async_client.send_sms(
                sender_id="Sender", message="Hi", contacts="255712345678"
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_sms_rate_limit(self, async_client):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(429, json={"error": "rate limited"})
        )
        with pytest.raises(KiboNetRateLimitError):
            await async_client.send_sms(
                sender_id="Sender", message="Hi", contacts="255712345678"
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_sms_server_error(self, async_client):
        # Non-JSON 5xx → KiboNetServerError
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(KiboNetServerError):
            await async_client.send_sms(
                sender_id="Sender", message="Hi", contacts="255712345678"
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_sms_business_error_as_5xx(self, async_client):
        # KiboNet returns 5xx with JSON success=false for business errors
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(
                501, json={"code": 501, "success": False, "message": "Sender id does not exists to your account.", "data": None}
            )
        )
        with pytest.raises(KiboNetAPIError, match="Sender id does not exists"):
            await async_client.send_sms(
                sender_id="INVALID", message="Hi", contacts="255712345678"
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_send_sms_api_error_success_false(self, async_client):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(
                200, json={"code": 400, "success": False, "message": "Bad request"}
            )
        )
        with pytest.raises(KiboNetAPIError, match="Bad request"):
            await async_client.send_sms(
                sender_id="Sender", message="Hi", contacts="255712345678"
            )


class TestAsyncGetDeliveryReport:

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_delivery_report(self, async_client, delivery_report_response):
        shoot_id = "abcd1234-5678-efgh-9012-ijklmnopqrst"
        respx.get(
            f"{BASE_URL}/api/v1/vendor/message/deliver/{shoot_id}"
        ).mock(return_value=httpx.Response(200, json=delivery_report_response))

        result = await async_client.get_delivery_report(shoot_id)
        assert result["success"] is True
        assert result["data"][0]["status"] == "Delivered"

    @pytest.mark.asyncio
    async def test_get_delivery_report_empty_shoot_id(self, async_client):
        with pytest.raises(KiboNetValidationError):
            await async_client.get_delivery_report("")


class TestAsyncGetBalance:

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_balance(self, async_client, balance_response):
        respx.get(f"{BASE_URL}/api/v1/vendor/message/balance").mock(
            return_value=httpx.Response(200, json=balance_response)
        )
        result = await async_client.get_balance()
        assert result["success"] is True
        assert result["data"]["totalSms"] == 30

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_balance_auth_error(self, async_client):
        respx.get(f"{BASE_URL}/api/v1/vendor/message/balance").mock(
            return_value=httpx.Response(401, json={"error": "unauthorised"})
        )
        with pytest.raises(KiboNetAuthenticationError):
            await async_client.get_balance()
