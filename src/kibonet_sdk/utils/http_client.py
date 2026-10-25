"""
Synchronous httpx client with connection pooling and retry logic.
"""

import logging
from typing import Optional, Any

import httpx

from ..exceptions import KiboNetConnectionError

logger = logging.getLogger(__name__)

BASE_URL = "https://sms.kibonet.co.tz"
SDK_VERSION = "0.1.1"


class HTTPClient:
    """
    Synchronous httpx client with connection pooling, retries, and header-based auth.

    Designed to be reused across multiple requests. Use as a context manager
    or call close() explicitly when done.
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 3,
        logger: Optional[logging.Logger] = None,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)

        transport = httpx.HTTPTransport(retries=max_retries)
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._build_headers(),
            timeout=timeout,
            transport=transport,
        )
        self.logger.debug(
            "KiboNet sync HTTP client initialised (base_url=%s, timeout=%s)",
            self.base_url,
            timeout,
        )

    def _build_headers(self) -> dict:
        return {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"KiboNet-Python-SDK/{SDK_VERSION}",
        }

    def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, …)
            endpoint: Path relative to base_url
            **kwargs: Extra arguments forwarded to httpx

        Returns:
            httpx.Response

        Raises:
            KiboNetConnectionError: On any network-level failure
        """
        url = f"/{endpoint.lstrip('/')}"
        self.logger.debug("→ %s %s", method, url)
        try:
            response = self._client.request(method, url, **kwargs)
            self.logger.debug("← %s", response.status_code)
            return response
        except httpx.TimeoutException as exc:
            self.logger.error("Request timed out: %s", exc)
            raise KiboNetConnectionError(
                f"Request timed out after {self.timeout}s"
            ) from exc
        except httpx.ConnectError as exc:
            self.logger.error("Connection error: %s", exc)
            raise KiboNetConnectionError(
                f"Failed to connect to KiboNet API: {exc}"
            ) from exc
        except httpx.RequestError as exc:
            self.logger.error("Request failed: %s", exc)
            raise KiboNetConnectionError(f"Request failed: {exc}") from exc

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()
        self.logger.debug("KiboNet sync HTTP client closed")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
