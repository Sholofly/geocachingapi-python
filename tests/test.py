"""Test for Geocaching Api integration."""
from geocachingapi import GeocachingApi, GeocachingStatus
import asyncio
import pytest

@pytest.mark.asyncio
async def test():
    status:GeocachingStatus = None
    token = "<insert token here>"
    api = GeocachingApi(token=token)
    status = await api.update()
    print(status.user.username)
    assert(status.user.username is not None)