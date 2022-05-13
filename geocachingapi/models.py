from __future__ import annotations
from enum import Enum
from typing import Any, Dict, Optional, TypedDict

from dataclasses import dataclass
from datetime import datetime
from .utils import try_get_from_dict

class GeocachingApiEnvironmentSettings(TypedDict):
    """Class to represent API environment settings"""
    api_scheme:str
    api_host:str
    api_port: int
    api_base_bath:str

class GeocachingApiEnvironment(Enum):
    """Enum to represent API environment"""
    Staging = 1,
    Production = 2,

class GeocachingSettings:
    """Class to hold the Geocaching Api settings"""
    fetch_trackables: bool
    environment: GeocachingApiEnvironment

    def __init__(self, fetch_trackables:bool = False, environment:GeocachingApiEnvironment = GeocachingApiEnvironment.Production ) -> None:
        """Initialize settings"""
        self.fetch_trackables = fetch_trackables

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

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update user from the API result"""
        self.reference_code = try_get_from_dict(data, "referenceCode", self.reference_code)
        self.username = try_get_from_dict(data, "username", self.username)
        self.find_count = try_get_from_dict(data, "findCount", self.find_count)
        self.hide_count = try_get_from_dict(data, "hideCount", self.hide_count)
        self.favorite_points = try_get_from_dict(data, "favoritePoints", self.favorite_points)
        self.souvenir_count = try_get_from_dict(data, "souvenirCount", self.souvenir_count)
        self.awarded_favorite_points = try_get_from_dict(data, "awardedFavoritePoints", self.awarded_favorite_points)

@dataclass
class GeocachingCoordinate:
    """Class to hold a Geocaching coordinate"""
    latitude: Optional[str] = None
    longitude: Optional[str] = None

    def __init__(self, *, data: Dict[str, Any]) -> GeocachingCoordinate:
        """Constructor for Geocaching coordinates"""
        self.latitude = try_get_from_dict(data, "latitude", None)
        self.longitude = try_get_from_dict(data, "longitude", None)

@dataclass
class GeocachingTrackableJourney:
    """Class to hold Geocaching trackable journey information"""
    coordinates: GeocachingCoordinate = None
    logged_date: Optional[datetime] = None

    def __init__(self, *, data: Dict[str, Any]) -> GeocachingTrackableJourney:
        """Constructor for Geocaching trackable journey"""
        if "coordinates" in data:
            self.coordinates = GeocachingCoordinate(data=data["coordinates"])
        else:
            self.coordinates = None
        self.logged_date = try_get_from_dict(data, "loggedDate", self.logged_date)

@dataclass
class GeocachingTrackable:
    """Class to hold the Geocaching trackable information"""
    reference_code: Optional[str] = None
    name: Optional[str] = None
    holder: GeocachingUser = None
    tracking_number: Optional[str] = None
    kilometers_traveled: Optional[str] = None
    miles_traveled: Optional[str] = None
    current_geocache_code: Optional[str] = None
    current_geocache_name: Optional[str] = None
    latest_journey: GeocachingTrackableJourney = None
    is_missing: bool = False
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update trackable from the API"""
        self.reference_code = try_get_from_dict(data, "referenceCode", self.reference_code)
        self.name = try_get_from_dict(data, "name", self.name)
        if data["holder"] is not None:
            if self.holder is None :
                holder = GeocachingUser()
            holder.update_from_dict(data["holder"])
        else:
            holder = None

        self.tracking_number = try_get_from_dict(data, "trackingNumber", self.tracking_number)
        self.kilometers_traveled = try_get_from_dict(data, "kilometersTraveled", self.kilometers_traveled)
        self.miles_traveled = try_get_from_dict(data, "milesTraveled", self.miles_traveled)
        self.current_geocache_code = try_get_from_dict(data, "currectGeocacheCode", self.current_geocache_code)
        self.current_geocache_name = try_get_from_dict(data, "currentGeocacheName", self.current_geocache_name)
        self.is_missing = try_get_from_dict(data, "isMissing", self.current_geocache_name)

class GeocachingStatus:
    """Class to hold all account status information"""
    user: GeocachingUser = None
    trackables: Dict[str, GeocachingTrackable] = None

    def __init__(self):
        """Initialize GeocachingStatus"""
        self.user = GeocachingUser()
        self.trackables = {}

    def update_user_from_dict(self, data: Dict[str, Any]) -> None:
        """Update user from the API result"""
        self.user.update_from_dict(data)
    
    def update_trackables_from_dict(self, data: Any) -> None:
        """Update trackables from the API result"""
        if not any(data):
            pass
        for trackable in data:
            reference_code = trackable["referenceCode"]
            if not reference_code in self.trackables.keys():
                self.trackables[reference_code] = GeocachingTrackable()
            self.trackables[reference_code].update_from_dict(trackable)
            