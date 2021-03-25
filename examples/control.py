"""Asynchronous Python client for the Geocaching API."""
import asyncio
from geocachingapi import GeocachingApi

async def main():
    """Show example of using the Geocaching API"""
    async with GeocachingApi() as api:
        print("test")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())