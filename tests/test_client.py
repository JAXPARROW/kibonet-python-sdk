"""
Tests for the synchronous KiboNetClient.
"""

import pytest
import respx
import httpx

from kibonet_sdk import KiboNetClient
from kibonet_sdk.exceptions import (
    KiboNetAuthenticationError,
    KiboNetAPIError,
    KiboNetConnectionError,
    KiboNetRateLimitError,
    KiboNetServerError,
    KiboNetValidationError,
)

BASE_URL = "https://sms.kibonet.co.tz"


class TestKiboNetClientInit:

    def test_rejects_empty_api_key(self):
        with pytest.raises(KiboNetValidationError):
            KiboNetClient(api_key="", api_secret="secret")

    def test_rejects_empty_api_secret(self):
        with pytest.raises(KiboNetValidationError):
            KiboNetClient(api_key="key", api_secret="")

    def test_context_manager(self):
        with KiboNetClient(api_key="k", api_secret="s") as c:
            assert c is not None


class TestIsHealthy:

    @respx.mock
    def test_healthy_returns_true(self, balance_response):
        respx.get(f"{BASE_URL}/api/v1/vendor/message/balance").mock(
            return_value=httpx.Response(200, json=balance_response)
        )
        client = KiboNetClient(api_key="k", api_secret="s")
        assert client.is_healthy() is True

    @respx.mock
    def test_unhealthy_returns_false(self):
        respx.get(f"{BASE_URL}/api/v1/vendor/message/balance").mock(
            return_value=httpx.Response(401, json={"error": "unauthorised"})
        )
        client = KiboNetClient(api_key="k", api_secret="s")
        assert client.is_healthy() is False

    def test_network_error_returns_false(self):
        client = KiboNetClient(api_key="k", api_secret="s")
        # Point to an unreachable host via monkeypatching
        client._http.base_url = "https://0.0.0.0"
        assert client.is_healthy() is False


class TestSendSMS:

    @respx.mock
    def test_send_sms_single_recipient(self, client, send_sms_response):
        route = respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(200, json=send_sms_response)
        )
        result = client.send_sms(
            sender_id="TestSender",
            message="Hello KiboNet!",
            contacts="255712345678",
        )
        assert result["success"] is True
        assert result["data"]["shootId"] == "abcd1234-5678-efgh-9012-ijklmnopqrst"
        assert route.called

    @respx.mock
    def test_send_sms_multiple_recipients(self, client, send_sms_response):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(200, json=send_sms_response)
        )
        result = client.send_sms(
            sender_id="TestSender",
            message="Bulk message",
            contacts=["255712345678", "255798765432"],
        )
        assert result["success"] is True

    @respx.mock
    def test_send_sms_with_delivery_url(self, client, send_sms_response):
        route = respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(200, json=send_sms_response)
        )
        client.send_sms(
            sender_id="Sender",
            message="Hello!",
            contacts="255712345678",
            delivery_report_url="https://myserver.com/callback",
        )
        request_body = route.calls.last.request.content
        assert b"deliveryReportUrl" in request_body

    def test_send_sms_empty_sender_raises(self, client):
        with pytest.raises(KiboNetValidationError):
            client.send_sms(sender_id="", message="Hi", contacts="255712345678")

    def test_send_sms_empty_message_raises(self, client):
        with pytest.raises(KiboNetValidationError):
            client.send_sms(sender_id="Sender", message="", contacts="255712345678")

    def test_send_sms_invalid_phone_raises(self, client):
        with pytest.raises(ValueError):
            client.send_sms(sender_id="Sender", message="Hi", contacts="bad_number")

    def test_send_sms_empty_contacts_raises(self, client):
        with pytest.raises(ValueError):
            client.send_sms(sender_id="Sender", message="Hi", contacts=[])

    @respx.mock
    def test_send_sms_auth_error(self, client):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(401, json={"error": "unauthorised"})
        )
        with pytest.raises(KiboNetAuthenticationError):
            client.send_sms(
                sender_id="Sender", message="Hi", contacts="255712345678"
            )

    @respx.mock
    def test_send_sms_rate_limit(self, client):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(429, json={"error": "rate limited"})
        )
        with pytest.raises(KiboNetRateLimitError):
            client.send_sms(
                sender_id="Sender", message="Hi", contacts="255712345678"
            )

    @respx.mock
    def test_send_sms_server_error(self, client):
        # Non-JSON 5xx → KiboNetServerError
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(KiboNetServerError):
            client.send_sms(
                sender_id="Sender", message="Hi", contacts="255712345678"
            )

    @respx.mock
    def test_send_sms_business_error_as_5xx(self, client):
        # KiboNet returns 5xx with JSON success=false for business errors
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(
                501, json={"code": 501, "success": False, "message": "Sender id does not exists to your account.", "data": None}
            )
        )
        with pytest.raises(KiboNetAPIError, match="Sender id does not exists"):
            client.send_sms(
                sender_id="INVALID", message="Hi", contacts="255712345678"
            )

    @respx.mock
    def test_send_sms_api_error_success_false(self, client):
        respx.post(f"{BASE_URL}/api/v1/vendor/message/send").mock(
            return_value=httpx.Response(
                200, json={"code": 400, "success": False, "message": "Bad request"}
            )
        )
        with pytest.raises(KiboNetAPIError, match="Bad request"):
            client.send_sms(
                sender_id="Sender", message="Hi", contacts="255712345678"
            )


class TestGetDeliveryReport:

    @respx.mock
    def test_get_delivery_report(self, client, delivery_report_response):
        shoot_id = "abcd1234-5678-efgh-9012-ijklmnopqrst"
        respx.get(
            f"{BASE_URL}/api/v1/vendor/message/deliver/{shoot_id}"
        ).mock(return_value=httpx.Response(200, json=delivery_report_response))

        result = client.get_delivery_report(shoot_id)
        assert result["success"] is True
        assert result["data"][0]["status"] == "Delivered"

    def test_get_delivery_report_empty_shoot_id(self, client):
        with pytest.raises(KiboNetValidationError):
            client.get_delivery_report("")


class TestGetBalance:

    @respx.mock
    def test_get_balance(self, client, balance_response):
        respx.get(f"{BASE_URL}/api/v1/vendor/message/balance").mock(
            return_value=httpx.Response(200, json=balance_response)
        )
        result = client.get_balance()
        assert result["success"] is True
        assert result["data"]["totalSms"] == 30

    @respx.mock
    def test_get_balance_auth_error(self, client):
        respx.get(f"{BASE_URL}/api/v1/vendor/message/balance").mock(
            return_value=httpx.Response(401, json={"error": "unauthorised"})
        )
        with pytest.raises(KiboNetAuthenticationError):
            client.get_balance()
