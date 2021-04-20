"""Test for Geocaching Api integration."""
from geocachingapi import GeocachingApi, GeocachingStatus, GeocachingSettings
#For adding your token add a file call token.py to current folder and add TOKEN = "<your token here>"
from .token import TOKEN
import asyncio
import pytest

# @pytest.mark.asyncio
import logging
logging.basicConfig(level=logging.DEBUG)

mylogger = logging.getLogger()

@pytest.mark.asyncio
async def test():
    status:GeocachingStatus = None
    api = GeocachingApi(token=TOKEN)
    status = await api.update()
    print(status.user.reference_code)
    assert(status.user.reference_code is not None)
    assert(status.user.find_count is not None)
    await api.close()
    assert(False)




