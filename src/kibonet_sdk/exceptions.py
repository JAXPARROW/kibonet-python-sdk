"""
Custom exception hierarchy for KiboNet SMS SDK.
All exceptions inherit from KiboNetError for easy catching.
"""


class KiboNetError(Exception):
    """Base exception for all KiboNet SDK errors"""
    pass


class KiboNetAuthenticationError(KiboNetError):
    """Invalid API key or secret (HTTP 401)"""
    pass


class KiboNetValidationError(KiboNetError):
    """Input validation failed (e.g., invalid phone number, empty message)"""
    pass


class KiboNetAPIError(KiboNetError):
    """API returned an error response"""
    def __init__(self, message: str, code: int = None, response_data: dict = None):
        super().__init__(message)
        self.code = code
        self.response_data = response_data or {}


class KiboNetRateLimitError(KiboNetAPIError):
    """Rate limit exceeded (HTTP 429)"""
    pass


class KiboNetInsufficientBalanceError(KiboNetAPIError):
    """Not enough SMS credits"""
    pass


class KiboNetConnectionError(KiboNetError):
    """Network-level error (timeout, DNS failure, TLS error)"""
    pass


class KiboNetServerError(KiboNetAPIError):
    """KiboNet server error (HTTP 5xx)"""
    pass
