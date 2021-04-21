"""Utils for consuming the API"""
from typing import Dict, Any, Callable, Optional

def try_get_from_dict(data: Dict[str, Any], key: str, original_value: Any, conversion: Optional[Callable[[Any], Any]] = None) -> Any:
    """Try to get value from dict, otherwise set default value"""
    if not key in data:
        return None
    
    value = data[key]
    if value is None:
        return original_value
    if conversion is None:
        return value 
    return conversion(value)
