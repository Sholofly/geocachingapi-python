"""Test for Geocaching Api integration."""
from geocachingapi import GeocachingApi, GeocachingStatus
import asyncio
import logging
from geocachingapi.models import GeocachingApiEnvironment
logging.basicConfig(level=logging.DEBUG)
from my_token import TOKEN
mylogger = logging.getLogger()

async def test():
    status:GeocachingStatus = None
    api = GeocachingApi(token=TOKEN, environment=GeocachingApiEnvironment.Staging)
    status = await api.update()
    print(status.user.reference_code)
    assert(status.user.reference_code is not None)
    assert(status.user.find_count is not None)
    await api.close()
    assert(False)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()

