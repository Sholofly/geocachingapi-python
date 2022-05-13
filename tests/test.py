"""Test for Geocaching Api integration."""
import asyncio
import logging
from geocachingapi import GeocachingApi, GeocachingStatus
from geocachingapi.models import GeocachingApiEnvironment, GeocachingSettings, GeocachingTrackable
from my_token import TOKEN
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger()

async def test():
    """Function to test GeocachingAPI integration"""
    status:GeocachingStatus = None
    api = GeocachingApi(token=TOKEN, environment=GeocachingApiEnvironment.Staging, settings = GeocachingSettings(fetch_trackables=True))
    status = await api.update()
    print(status.user.reference_code)
    for trackable in status.trackables.values():
        print('----------------------')
        print(f'Trackable code: {trackable.reference_code}')
        print(f'Trackable name: {trackable.name}')
        print(f'Kilometers traveled: {trackable.kilometers_traveled}km')
        print(f'Miles traveled: {trackable.miles_traveled}mi')
        print(f'Missing?: {trackable.is_missing}')
        if trackable.latest_journey:
            print(f'last log: {trackable.latest_journey.logged_date}')
            print(f'latitude: {trackable.latest_journey.coordinates.latitude}')
            print(f'longitude: {trackable.latest_journey.coordinates.longitude}')
    await api.close()
loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
