"""Test for Geocaching Api integration."""
from geocachingapi import GeocachingApi, GeocachingStatus
#For adding your token add a file call token.py to current folder and add TOKEN = "<your token here>"
from .token import TOKEN
import asyncio
import pytest

@pytest.mark.asyncio
async def test():
    status:GeocachingStatus = None
    api = GeocachingApi(token=TOKEN)
    status = await api.update()

    assert(status.user.username is not None)
    assert(status.user.find_count is not None)