"""Class for managing one Geocaching API integration."""
from __future__ import annotations

import asyncio
import json
import socket
import async_timeout
import backoff
from yarl import URL
from aiohttp import ClientResponse, ClientSession, ClientError

from typing import Any, Awaitable, Callable, Dict, List, Optional
from .const import (
    GEOCACHING_API_BASE_PATH,
    GEOCACHING_API_HOST,
    GEOCACHING_API_PORT,
    GEOCACHING_API_SCHEME,
    GEOCACHING_API_VERSION,
)
from .exceptions import (
    GeocachingApiConnectionError,
    GeocachingApiConnectionTimeoutError,
    GeocachingApiError,
    GeocachingApiRateLimitError,
)

from .models import (
    GeocachingStatus,
)

class GeocachingApi:

    _close_session: bool = False
    _status: GeocachingStatus = GeocachingStatus()
    def __init__(
        self,
        *,
        token: str,
        request_timeout: int = 8,
        session: Optional[ClientSession] = None,
        token_refresh_method: Optional[Callable[[], Awaitable[str]]] = None,
    ) -> None:
        """Initialize connection with the Geocaching API."""
        self._session = session
        self.request_timeout = request_timeout
        self.token = token
        self.token_refresh_method = token_refresh_method

    @backoff.on_exception(backoff.expo, GeocachingApiConnectionError, max_tries=3, logger=None)
    @backoff.on_exception(
        backoff.expo, GeocachingApiRateLimitError, base=60, max_tries=6, logger=None
    )
    async def _request(self, method, uri, **kwargs) -> ClientResponse:
        """Make a request."""
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()
        
        url = URL.build(
            scheme=GEOCACHING_API_SCHEME,
            host=GEOCACHING_API_HOST,
            port=GEOCACHING_API_PORT,
            path=GEOCACHING_API_BASE_PATH,
        ).join(URL(uri))
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        headers["Authorization"] = f"Bearer {self.token}"

        if self._session is None:
            self._session = ClientSession()
            self._close_session = True

        try:
            with async_timeout.timeout(self.request_timeout):
                response =  await self._session.request(
                    method,
                    f"{url}",
                    **kwargs,
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
            raise GeocachingApiConnectionTimeoutError(
                "Timeout occurred while connecting to the Geocaching API"
            ) from exception
        except (ClientError, socket.gaierror) as exception:
            raise GeocachingApiConnectionError(
                "Error occurred while communicating with the Geocaching API"
            ) from exception
        
        content_type = response.headers.get("Content-Type", "")
        # Error handling
        if (response.status // 100) in [4, 5]:
            contents = await response.read()
            response.close()

            if response.status == 429:
                raise GeocachingApiRateLimitError(
                    "Rate limit error has occurred with the Geocaching API"
                )

            if content_type == "application/json":
                raise GeocachingApiError(response.status, json.loads(contents.decode("utf8")))
            raise GeocachingApiError(response.status, {"message": contents.decode("utf8")})
        
        # Handle empty response
        if response.status == 204:
            return

        if "application/json" in content_type:
            return await response.json()
        return await response.text()

    async def update(self) -> GeocachingStatus:
        await self._update_user(None)
        return self._status
        
    async def _update_user(self, data: Dict[str, Any] = None) -> None:
        assert self._status
        if data is None:
            fields = ",".join([
                "username",
                "referenceCode",
                "findCount",
                "hideCount",
                "favoritePoints",
                "souvenirCount",
                "awardedFavoritePoints"
            ])
            data = await self._request("GET", f"/{GEOCACHING_API_VERSION}/users/me?fields={fields}")
        self._status.user.update_from_dict(data)
    
    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()
    
    async def __aenter__(self) -> GeocachingApi:
        """Async enter."""
        return self
    
    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()