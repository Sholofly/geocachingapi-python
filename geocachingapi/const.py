"""Geocaching Api Constants."""
from .models import GeocachingApiEnvironment, GeocachingApiEnvironmentSettings

ENVIRONMENT_SETTINGS = {
    GeocachingApiEnvironment.Staging : GeocachingApiEnvironmentSettings(   
            api_scheme= "https",
            api_host= "staging.api.groundspeak.com",
            api_port = 443,
            api_base_bath="/v1",
            ),
            
    GeocachingApiEnvironment.Production : GeocachingApiEnvironmentSettings(   
            api_scheme= "https",
            api_host= "api.groundspeak.com",
            api_port = 443,
            api_base_bath="/v1",
            )
}

MEMBERSHIP_LEVELS = {
    0: "Unknown",
    1: "Basic",
    2: "Charter",
    3: "Premium"
}

# Required parameters for fetching caches in order to generate complete GeocachingCache objects
CACHE_FIELDS_PARAMETER: str = ",".join([
                "referenceCode",
                "name",
                "owner",
                "postedCoordinates",
                "url",
                "favoritePoints",
                "userData",
                "placedDate",
                "location"
            ])
