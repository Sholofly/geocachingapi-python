from __future__ import annotations
from enum import Enum
from typing import Any, Dict, Optional, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
from math import radians, sin, cos, acos

from geocachingapi.limits import MAXIMUM_TRACKED_CACHES, MAXIMUM_TRACKED_TRACKABLES
from geocachingapi.exceptions import GeocachingTooManyCodesError
from .utils import try_get_from_dict
import reverse_geocode
import asyncio

# Parser that parses an ISO date string to a date (not datetime)
DATE_PARSER = lambda d: datetime.date(datetime.fromisoformat(d))

def try_get_user_from_dict(data: Dict[str, Any], key: str, original_value: Any) -> GeocachingUser | None:
    """Try to get user from dict, otherwise set default value"""
    user_data = try_get_from_dict(data, key, None)
    if user_data is None:
        return original_value
    
    user = GeocachingUser()
    user.update_from_dict(data[key])
    return user

class GeocachingApiEnvironmentSettings(TypedDict):
    """Class to represent API environment settings"""
    api_scheme: str
    api_host: str
    api_port: int
    api_base_bath: str

class GeocachingApiEnvironment(Enum):
    """Enum to represent API environment"""
    Staging = 1
    Production = 2

@dataclass
class NearbyCachesSetting:
    """Class to hold the nearby caches settings, as part of the API settings"""
    location: GeocachingCoordinate # The position from which to search for nearby caches
    radius_km: float # The radius around the position to search
    max_count: int # The max number of nearby caches to return

    def __init__(self, location: GeocachingCoordinate, radiusKm: float, maxCount: int) -> None:
        self.location = location
        self.radius_km = radiusKm
        self.max_count = max(0, round(maxCount))

class GeocachingSettings:
    """Class to hold the Geocaching API settings"""
    tracked_cache_codes: set[str]
    tracked_trackable_codes: set[str]
    environment: GeocachingApiEnvironment
    nearby_caches_setting: NearbyCachesSetting

    def __init__(self, trackable_codes: set[str] = [], cache_codes: set[str] = [], nearby_caches_setting: NearbyCachesSetting = None) -> None:
        """Initialize settings"""
        self.tracked_trackable_codes = trackable_codes
        self.tracked_cache_codes = cache_codes
        self.nearby_caches_setting = nearby_caches_setting

    def set_tracked_caches(self, cache_codes: set[str]):
        # Ensure the number of tracked caches are within the limits
        if len(cache_codes) > MAXIMUM_TRACKED_CACHES:
            raise GeocachingTooManyCodesError(f"Number of tracked caches cannot exceed 50. Was: {len(cache_codes)}")
        self.tracked_cache_codes = cache_codes

    def set_tracked_trackables(self, trackable_codes: set[str]):
        # Ensure the number of tracked trackables are within the limits
        if len(trackable_codes) > MAXIMUM_TRACKED_TRACKABLES:
            raise GeocachingTooManyCodesError(f"Number of tracked trackables cannot exceed 50. Was: {len(trackable_codes)}")
        self.tracked_trackable_codes = trackable_codes

    def set_nearby_caches_setting(self, setting: NearbyCachesSetting):
        self.nearby_caches_setting = setting

@dataclass
class GeocachingUser:
    """Class to hold the Geocaching user information"""
    reference_code: Optional[str] = None
    username: Optional[str] = None
    find_count: Optional[int] = None
    hide_count: Optional[int] = None
    favorite_points: Optional[int] = None
    souvenir_count: Optional[int] = None
    awarded_favorite_points: Optional[int] = None
    membership_level_id: Optional[int] = None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update user from the API result"""
        self.reference_code = try_get_from_dict(data, "referenceCode", self.reference_code)
        self.username = try_get_from_dict(data, "username", self.username)
        self.find_count = try_get_from_dict(data, "findCount", self.find_count)
        self.hide_count = try_get_from_dict(data, "hideCount", self.hide_count)
        self.favorite_points = try_get_from_dict(data, "favoritePoints", self.favorite_points)
        self.souvenir_count = try_get_from_dict(data, "souvenirCount", self.souvenir_count)
        self.awarded_favorite_points = try_get_from_dict(data, "awardedFavoritePoints", self.awarded_favorite_points)
        self.membership_level_id = try_get_from_dict(data, "membershipLevelId", self.membership_level_id)

@dataclass
class GeocachingCoordinate:
    """Class to hold a Geocaching coordinate"""
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    def __init__(self, *, data: Dict[str, Any]) -> GeocachingCoordinate:
        """Constructor for Geocaching coordinates"""
        self.latitude = try_get_from_dict(data, "latitude", None)
        self.longitude = try_get_from_dict(data, "longitude", None)

    def get_distance_km(coord1: GeocachingCoordinate, coord2: GeocachingCoordinate) -> float:
        """Returns the distance in kilometers between two coordinates. Returns the great-circle distance between the coordinates"""
        mlat: float = radians(float(coord1.latitude))
        mlon: float = radians(float(coord1.longitude))
        plat: float = radians(float(coord2.latitude))
        plon: float = radians(float(coord2.longitude))
        earth_radius_km: float = 6371.01
        return earth_radius_km * acos(sin(mlat) * sin(plat) + cos(mlat) * cos(plat) * cos(mlon - plon))

@dataclass
class GeocachingTrackableJourney:
    """Class to hold Geocaching trackable journey information"""
    coordinates: GeocachingCoordinate = None # The location at the end of this journey
    location_name: Optional[str] = None # A reverse geocoded name of the location at the end of this journey
    distance_km: Optional[float] = None # The distance the trackable travelled in this journey
    date: Optional[datetime] = None # The date when this journey was completed
    user: GeocachingUser = None # The Geocaching user who moved the trackable during this journey
    cache_name: Optional[str] = None # The name of the cache the trackable resided in at the end of this journey
    url: Optional[str] = None # A link to this journey

    # Note: Reverse geocoding the journeys is not performed in the init function as it is an asynchronous operation
    def __init__(self, *, data: Dict[str, Any]) -> None:
        """Constructor for Geocaching trackable journey"""
        if "coordinates" in data and data["coordinates"] is not None:
            self.coordinates = GeocachingCoordinate(data=data["coordinates"])
        else:
            self.coordinates = None
        self.date = try_get_from_dict(data, "loggedDate", self.date, DATE_PARSER)
        self.user = try_get_user_from_dict(data, "owner", self.user)
        self.cache_name = try_get_from_dict(data, "geocacheName", self.cache_name)
        self.url = try_get_from_dict(data, "url", self.url)

    @classmethod
    async def from_list(cls, data_list: list[Dict[str, Any]]) -> list[GeocachingTrackableJourney]:
        """Creates a list of GeocachingTrackableJourney instances from an array of data, in order from oldest to newest"""
        journeys: list[GeocachingTrackableJourney] = sorted([cls(data=data) for data in data_list], key=lambda j: j.date, reverse=False)
        
        # Reverse geocoding the journey locations reads from a file and is therefore a blocking call
        # Therefore, we go over all journeys and perform the reverse geocoding pass after they have been initialized
        loop = asyncio.get_running_loop()
        for journey in journeys:
            # Get the location information from the `reverse_geocode` package
            location_info: dict[str, Any] = await loop.run_in_executor(None, reverse_geocode.get, (journey.coordinates.latitude, journey.coordinates.longitude))
            
            # Parse the response to extract the relevant data
            location_city: str = try_get_from_dict(location_info, "city", "Unknown")
            location_country: str = try_get_from_dict(location_info, "country", "Unknown")
            
            # Set the location name to a formatted string
            journey.location_name = f"{location_city}, {location_country}"
        
        return journeys

@dataclass
class GeocachingTrackableLog:
    reference_code: Optional[str] = None
    owner: GeocachingUser = None
    text: Optional[str] = None
    log_type: Optional[str] = None
    logged_date: Optional[datetime] = None

    def __init__(self, *, data: Dict[str, Any]) -> GeocachingTrackableLog:
        self.reference_code = try_get_from_dict(data, "referenceCode", self.reference_code)
        self.owner = try_get_user_from_dict(data, "owner", self.owner)
        self.log_type = try_get_from_dict(data["trackableLogType"], "name", self.log_type)
        self.logged_date = try_get_from_dict(data, "loggedDate", self.logged_date)
        self.text = try_get_from_dict(data, "text", self.text)


@dataclass
class GeocachingTrackable:
    """Class to hold the Geocaching trackable information"""
    reference_code: Optional[str] = None
    name: Optional[str] = None
    holder: GeocachingUser = None
    owner: GeocachingUser = None
    url: Optional[str] = None
    release_date: Optional[datetime.date] = None
    tracking_number: Optional[str] = None
    kilometers_traveled: Optional[float] = None
    miles_traveled: Optional[float] = None
    current_geocache_code: Optional[str] = None
    current_geocache_name: Optional[str] = None
    journeys: Optional[list[GeocachingTrackableJourney]] = field(default_factory=list)
    coordinates: GeocachingCoordinate = None

    is_missing: bool = False
    trackable_type: str = None
    latest_log: GeocachingTrackableLog = None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update trackable from the API"""
        self.reference_code = try_get_from_dict(data, "referenceCode", self.reference_code)
        self.name = try_get_from_dict(data, "name", self.name)
        self.holder = try_get_user_from_dict(data, "holder", self.holder)
        self.owner = try_get_user_from_dict(data, "owner", self.owner)
        self.url = try_get_from_dict(data, "url", self.url)
        self.release_date = try_get_from_dict(data, "releasedDate", self.release_date, DATE_PARSER)
        self.tracking_number = try_get_from_dict(data, "trackingNumber", self.tracking_number)
        self.kilometers_traveled = try_get_from_dict(data, "kilometersTraveled", self.kilometers_traveled, float)
        self.miles_traveled = try_get_from_dict(data, "milesTraveled", self.miles_traveled, float)
        self.current_geocache_code = try_get_from_dict(data, "currentGeocacheCode", self.current_geocache_code)
        self.current_geocache_name = try_get_from_dict(data, "currentGeocacheName", self.current_geocache_name)
        self.is_missing = try_get_from_dict(data, "isMissing", self.is_missing)
        self.trackable_type = try_get_from_dict(data, "type", self.trackable_type)
        
        if "trackableLogs" in data and len(data["trackableLogs"]) > 0:
            self.latest_log = GeocachingTrackableLog(data=data["trackableLogs"][0])

@dataclass
class GeocachingCache:
    reference_code: Optional[str] = None
    name: Optional[str] = None
    owner: GeocachingUser = None
    coordinates: GeocachingCoordinate = None
    url: Optional[str] = None
    favorite_points: Optional[int] = None
    hidden_date: Optional[datetime.date] = None
    found_date_time: Optional[datetime] = None
    found_by_user: Optional[bool] = None
    location: Optional[str] = None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        self.reference_code = try_get_from_dict(data, "referenceCode", self.reference_code)
        self.name = try_get_from_dict(data, "name", self.name)
        self.owner = try_get_user_from_dict(data, "owner", self.owner)
        self.url = try_get_from_dict(data, "url", self.url)
        self.favorite_points = try_get_from_dict(data, "favoritePoints", self.favorite_points, int)
        self.hidden_date = try_get_from_dict(data, "placedDate", self.hidden_date, DATE_PARSER)

        # Parse the user data (information about this cache, specific to the user)
        # The value is in data["userData"]["foundDate"], and is either None (not found) or a `datetime` object
        if "userData" in data:
            user_data_obj: Dict[Any] = try_get_from_dict(data, "userData", {})
            found_date_time: datetime | None = try_get_from_dict(user_data_obj, "foundDate", None, lambda d: None if d is None else datetime.fromisoformat(d))
            self.found_date_time = found_date_time
            self.found_by_user = found_date_time is not None
        else:
            self.found_date_time = None
            self.found_by_user = None
        
        # Parse the location
        # Returns the location as "State, Country" if either could be parsed
        location_obj: Dict[Any] = try_get_from_dict(data, "location", {})
        location_state: str = try_get_from_dict(location_obj, "state", "Unknown")
        location_country: str = try_get_from_dict(location_obj, "country", "Unknown")
        # Set the location to `None` if both state and country are unknown, otherwise set it to the known data
        self.location = None if set([location_state, location_country]) == {"Unknown"} else f"{location_state}, {location_country}"
        
        if "postedCoordinates" in data:
            self.coordinates = GeocachingCoordinate(data=data["postedCoordinates"])
        else:
            self.coordinates = None

class GeocachingStatus:
    """Class to hold all account status information"""
    user: GeocachingUser = None
    trackables: Dict[str, GeocachingTrackable] = None
    nearby_caches: list[GeocachingCache] = []
    tracked_caches: list[GeocachingCache] = []

    def __init__(self):
        """Initialize GeocachingStatus"""
        self.user = GeocachingUser()
        self.trackables = {}
        self.nearby_caches = []
        self.tracked_caches = []

    def update_user_from_dict(self, data: Dict[str, Any]) -> None:
        """Update user from the API result"""
        self.user.update_from_dict(data)

    def update_caches(self, data: Any) -> None:
        """Update caches from the API result"""
        if not any(data):
           pass

        self.tracked_caches = GeocachingStatus.parse_caches(data)

    def update_trackables_from_dict(self, data: Any) -> None:
        """Update trackables from the API result"""
        if not any(data):
            pass
        
        for trackable in data:
            reference_code = trackable["referenceCode"]
            if not reference_code in self.trackables.keys():
                self.trackables[reference_code] = GeocachingTrackable()
            self.trackables[reference_code].update_from_dict(trackable)
    
    def update_nearby_caches_from_dict(self, data: Any) -> None:
        """Update nearby caches from the API result"""
        if not any(data):
            pass

        self.nearby_caches = GeocachingStatus.parse_caches(data)
    
    @staticmethod
    def parse_caches(data: Any) -> list[GeocachingCache]:
        """Parse caches from the API result"""
        if data is None:
            return []
        
        caches: list[GeocachingCache] = []
        for cache_data in data:
            cache = GeocachingCache()
            cache.update_from_dict(cache_data)
            caches.append(cache)
        
        return caches