from typing import Optional, Union


class SocietyEvent():
    def __init__(self, title : Optional[str] = None, long_text : Optional[str] = None,
                 short_text : Optional[str] = None, start : Optional[float] = None,
                 end : Optional[float] = None, place : Optional[Union[str, int]] = None, image = None):
        self.title = title
        self.place = place
        self.start = start
        self.end = end
        self.long_text = long_text
        self.short_text = short_text
        self.image = image