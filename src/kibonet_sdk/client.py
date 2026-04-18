"""
Synchronous KiboNet SMS client.
"""

import logging
from typing import Any, Dict, List, Optional, Union

import httpx

from .exceptions import (
    KiboNetAPIError,
    KiboNetAuthenticationError,
    KiboNetConnectionError,
    KiboNetRateLimitError,
    KiboNetServerError,
    KiboNetValidationError,
)
from .utils.http_client import HTTPClient
from .utils.validators import PhoneNumberValidator


_SEND_ENDPOINT = "api/v1/vendor/message/send"
_DELIVER_ENDPOINT = "api/v1/vendor/message/deliver/{shoot_id}"
_BALANCE_ENDPOINT = "api/v1/vendor/message/balance"


class KiboNetClient:
    """
    Synchronous client for the KiboNet SMS API.

    Supports:
    - Sending SMS to one or multiple recipients
    - Retrieving delivery reports by shoot ID
    - Checking your SMS balance
    - Health-check via the balance endpoint

    Example::

        from kibonet_sdk import KiboNetClient

        with KiboNetClient(api_key="...", api_secret="...") as client:
            if client.is_healthy():
                resp = client.send_sms(
                    sender_id="MyBrand",
                    message="Hello from KiboNet!",
                    contacts=["255712345678", "255798765432"],
                    delivery_report_url="https://myserver.com/delivery",
                )
                print(resp["data"]["shootId"])
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialise the KiboNet synchronous client.

        Args:
            api_key: API key from the KiboNet portal.
            api_secret: API secret from the KiboNet portal.
            timeout: Per-request timeout in seconds (default 30).
            max_retries: Number of automatic retries on transient errors (default 3).
            logger: Optional custom :class:`logging.Logger`.
        """
        if not api_key or not isinstance(api_key, str):
            raise KiboNetValidationError("api_key must be a non-empty string")
        if not api_secret or not isinstance(api_secret, str):
            raise KiboNetValidationError("api_secret must be a non-empty string")

        self.logger = logger or logging.getLogger(__name__)
        self._http = HTTPClient(
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            max_retries=max_retries,
            logger=self.logger,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_healthy(self) -> bool:
        """
        Check whether the KiboNet API is reachable and credentials are valid.

        Never raises — always returns a boolean.  Suitable for liveness /
        readiness probes in containerised deployments.

        Returns:
            ``True`` if the API responds with HTTP 200, ``False`` otherwise.
        """
        try:
            response = self._http.request("GET", _BALANCE_ENDPOINT, timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    def send_sms(
        self,
        sender_id: str,
        message: str,
        contacts: Union[str, List[str]],
        delivery_report_url: str = "",
        message_type: str = "text",
    ) -> Dict[str, Any]:
        """
        Send a text SMS to one or more recipients.

        Args:
            sender_id: Sender name/ID displayed to recipients.
            message: Text content of the SMS.
            contacts: A single phone number, a list of phone numbers, or an
                      already comma-separated string.
            delivery_report_url: Optional callback URL for delivery status updates.
            message_type: Message type — currently only ``"text"`` is supported.

        Returns:
            Parsed API response dict, e.g.::

                {
                    "code": 200,
                    "data": {
                        "validContacts": 2,
                        "invalidContacts": 0,
                        "duplicatedContacts": 0,
                        "messageSize": 20,
                        "message": "Hello!",
                        "shootId": "abcd1234-…"
                    },
                    "success": True,
                    "message": "Message submit"
                }

        Raises:
            KiboNetValidationError: Invalid input parameters.
            KiboNetAuthenticationError: Invalid credentials.
            KiboNetRateLimitError: Rate limit exceeded.
            KiboNetServerError: KiboNet server error.
            KiboNetAPIError: Any other API-level error.
            KiboNetConnectionError: Network failure.
        """
        if not sender_id or not isinstance(sender_id, str):
            raise KiboNetValidationError("sender_id must be a non-empty string")
        if not message or not isinstance(message, str):
            raise KiboNetValidationError("message must be a non-empty string")

        contacts_csv = PhoneNumberValidator.to_csv(contacts)

        payload: Dict[str, Any] = {
            "senderId": sender_id,
            "messageType": message_type,
            "message": message,
            "contacts": contacts_csv,
        }
        if delivery_report_url:
            payload["deliveryReportUrl"] = delivery_report_url

        response = self._http.request("POST", _SEND_ENDPOINT, json=payload)
        return self._handle_response(response)

    def get_delivery_report(self, shoot_id: str) -> Dict[str, Any]:
        """
        Retrieve delivery status reports for a previously sent message.

        Args:
            shoot_id: The ``shootId`` returned by :meth:`send_sms`.

        Returns:
            Parsed API response dict, e.g.::

                {
                    "code": 200,
                    "data": [
                        {
                            "message": "Hello!",
                            "mobile": "255712345678",
                            "senderId": "MyBrand",
                            "status": "Delivered",
                            "statusCode": "000",
                            "explanation": "N/A",
                            "messageType": "text",
                            "sentAt": "07-02-2024 07:35:08"
                        }
                    ],
                    "success": True,
                    "message": "Sent messages report"
                }

        Raises:
            KiboNetValidationError: If ``shoot_id`` is empty.
            KiboNetAuthenticationError: Invalid credentials.
            KiboNetAPIError: Any other API-level error.
            KiboNetConnectionError: Network failure.
        """
        if not shoot_id or not isinstance(shoot_id, str):
            raise KiboNetValidationError("shoot_id must be a non-empty string")

        endpoint = _DELIVER_ENDPOINT.format(shoot_id=shoot_id)
        response = self._http.request("GET", endpoint)
        return self._handle_response(response)

    def get_balance(self) -> Dict[str, Any]:
        """
        Check the current SMS credit balance for your account.

        Returns:
            Parsed API response dict, e.g.::

                {
                    "code": 200,
                    "data": {"totalSms": 30},
                    "success": True,
                    "message": "Balance"
                }

        Raises:
            KiboNetAuthenticationError: Invalid credentials.
            KiboNetAPIError: Any other API-level error.
            KiboNetConnectionError: Network failure.
        """
        response = self._http.request("GET", _BALANCE_ENDPOINT)
        return self._handle_response(response)

    # ------------------------------------------------------------------
    # Resource management
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close underlying HTTP connections and free resources."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Map HTTP / API error codes to SDK exceptions."""
        if response.status_code == 401:
            raise KiboNetAuthenticationError(
                "Authentication failed — check your api_key and api_secret"
            )
        if response.status_code == 429:
            raise KiboNetRateLimitError("Rate limit exceeded", code=429)

        # Always try to parse JSON first — KiboNet uses 5xx for business errors too
        try:
            data = response.json()
        except Exception:
            if 500 <= response.status_code < 600:
                raise KiboNetServerError(
                    f"KiboNet server error (HTTP {response.status_code})",
                    code=response.status_code,
                )
            raise KiboNetAPIError(
                f"Unexpected non-JSON response (HTTP {response.status_code}): "
                f"{response.text[:200]}"
            )

        if not data.get("success", False):
            raise KiboNetAPIError(
                data.get("message", f"API error (HTTP {response.status_code})"),
                code=data.get("code"),
                response_data=data,
            )

        return data
