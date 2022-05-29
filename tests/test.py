"""Test for Geocaching Api integration."""
import asyncio
import logging
from geocachingapi import GeocachingApi
from geocachingapi.models import GeocachingApiEnvironment, GeocachingSettings
from my_token import TOKEN
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger()

async def test():
    """Function to test GeocachingAPI integration"""
    gc_settings = GeocachingSettings()
    api = GeocachingApi(token=TOKEN, environment=GeocachingApiEnvironment.Staging, settings=gc_settings)
    gc_settings.set_trackables(['TB87DTF'])
    await api.update_settings(gc_settings)
    await _update(api)
    await api.close()


async def _update(api:GeocachingApi):
    """Update and print"""
    status = await api.update()
    print(status.user.reference_code)
    for trackable in status.trackables.values():
        print('----------------------')
        print(f'Trackable code: {trackable.reference_code}')
        print(f'Trackable name: {trackable.name}')
        print(f'Trackable type: {trackable.trackable_type}')
        print(f'Kilometers traveled: {trackable.kilometers_traveled}km')
        print(f'Miles traveled: {trackable.miles_traveled}mi')
        print(f'Missing?: {trackable.is_missing}')
        if trackable.latest_journey:
            print(f'last journey: {trackable.latest_journey.logged_date}')
            print(f'latitude: {trackable.latest_journey.coordinates.latitude}')
            print(f'longitude: {trackable.latest_journey.coordinates.longitude}')
        if trackable.latest_log:
            print(f'last log date: {trackable.latest_log.logged_date}')
            print(f'last log type: {trackable.latest_log.log_type}')
            print(f'last log username: {trackable.latest_log.owner.username}')
            print(f'last log text: {trackable.latest_log.text}')
        

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
