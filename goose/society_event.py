from datetime import datetime
from typing import Optional, Union

from extended_properties import ExtendedProperties

class SocietyEvent():
    def __init__(self, *, title : Optional[str] = None, long_text : Optional[str] = None,
                 short_text : Optional[str] = None, start : Optional[datetime] = None,
                 end : Optional[datetime] = None, location : Optional[Union[str, int]] = None,
                 image : Optional[bytes] = None, is_requesting_image : bool = False,
                 id : Optional[str] = None, props: Optional[ExtendedProperties] = None):
        self.title = title
        self.location = location
        self.start = start
        self.end = end
        self.long_text = long_text
        self.short_text = short_text
        self.image = image
        self.is_requesting_image = is_requesting_image
        self.id = id
        self.props = props
    
    def has_physical_location(self) -> bool:
        return isinstance(self.location, str)