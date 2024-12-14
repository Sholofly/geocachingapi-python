"""Exceptions for the Geocaching API."""

class GeocachingApiError(Exception):
    """Generic GeocachingApi exception."""

class GeocachingInvalidSettingsError(Exception):
    """GeocachingApi invalid settings exception."""
    def __init__(self, code_type: str, invalid_codes: set[str]):
        super().__init__(f"Invalid {code_type} codes: {', '.join(invalid_codes)}")

class GeocachingTooManyCodesError(GeocachingApiError):
    """GeocachingApi settings exception: too many codes."""
    def __init__(self, message: str):
        super().__init__(message)

class GeocachingApiConnectionError(GeocachingApiError):
    """GeocachingApi connection exception."""


class GeocachingApiConnectionTimeoutError(GeocachingApiConnectionError):
    """GeocachingApi connection timeout exception."""


class GeocachingApiRateLimitError(GeocachingApiConnectionError):
    """GeocachingApi Rate Limit exception."""
    