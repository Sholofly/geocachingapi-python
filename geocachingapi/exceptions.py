"""Exceptions for the Gecaching API."""

class GeocachingApiError(Exception):
    """Generic GeocachingApi exception."""


class GeocachingApiConnectionError(GeocachingApiError):
    """GeocachingApi connection exception."""


class GeocachingApiConnectionTimeoutError(GeocachingApiConnectionError):
    """GeocachingApi connection timeout exception."""


class GeocachingApiRateLimitError(GeocachingApiConnectionError):
    """GeocachingApi Rate Limit exception."""
    