"""Asynchronous Python client for the Geocaching API."""
import asyncio
from geocachingapi import GeocachingApi
from geocachingapi.models import GeocachingApiEnvironment

async def main():
    """Show example of using the Geocaching API"""
    async with GeocachingApi(token="<insert your token here>", environment=GeocachingApiEnvironment.Staging) as api:
        status = await api.update()
        print(status.user.reference_code)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    