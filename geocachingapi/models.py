from __future__ import annotations
from typing import Any, Callable, Dict, Optional

from dataclasses import dataclass

@dataclass
class GeocachingUser:
    reference_code: Optional[str] = None
    username: Optional[str] = None
    find_count: Optional[int] = None
    hide_count: Optional[int] = None
    favorite_points: Optional[int] = None
    souvenir_count: Optional[int] = None
    awarded_favorite_points: Optional[int] = None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        if  "username" in data:
            self.username = data["username"]
        if  "reference" in data:
            self.reference_code = data["referenceCode"]
        if  "findCount" in data:
            self.find_count = data["findCount"]
        if  "hideCount" in data:
            self.hide_count = data["hideCount"]
        if  "favoritePoints" in data:
            self.favorite_points = data["favoritePoints"]
        if  "souvenirCount" in data:
            self.souvenir_count = data["souvenirCount"]
        if  "awardedFavoritePoints" in data:
            self.awarded_favorite_points = data["awardedFavoritePoints"]

        pass

class GeocachingStatus:
    user: GeocachingUser = GeocachingUser()
    def __init__(self) -> None:
        pass

    def update_from_dict(self, data: Dict[str, Any]) -> GeocachingStatus:
        return self