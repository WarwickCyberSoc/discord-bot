from typing import Optional, Union

class SocietyEvent():
    def __init__(self, title : Optional[str] = None, long_text : Optional[str] = None,
                 short_text : Optional[str] = None, start : Optional[int] = None,
                 end : Optional[int] = None, place : Optional[Union[str, int]] = None,
                 image = None, is_requesting_image : bool = False):
        self.title = title
        self.location = place
        self.start = start
        self.end = end
        self.long_text = long_text
        self.short_text = short_text
        self.image = image
        self.is_requesting_image = is_requesting_image