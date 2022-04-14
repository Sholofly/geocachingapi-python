"""Test for Geocaching Api integration."""
import asyncio
import logging
from geocachingapi import GeocachingApi, GeocachingStatus
from geocachingapi.models import GeocachingApiEnvironment, GeocachingSettings
from my_token import TOKEN
logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()

async def test():
    """Function to test GeocachingAPI  integration"""
    status:GeocachingStatus = None
    api = GeocachingApi(token=TOKEN, environment=GeocachingApiEnvironment.Staging, settings = GeocachingSettings(fetch_trackables=True))
    status = await api.update()
    print(status.user.reference_code)
    await api.close()
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
