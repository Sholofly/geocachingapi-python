from __future__ import annotations
from typing import Any, Callable, Dict, Optional

from dataclasses import dataclass

@dataclass
class GeocachingUser:
    username: Optional[str] = None
    reference_code: Optional[str] = None

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        if  "username" in data:
            self.username = data["username"]
        if  "reference" in data:
            self.reference_code = data["referenceCode"]

        pass

class GeocachingStatus:
    user: GeocachingUser = GeocachingUser()
    def __init__(self) -> None:
        pass

    def update_from_dict(self, data: Dict[str, Any]) -> GeocachingStatus:
        return self