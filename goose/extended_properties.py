from typing import Union

class ExtendedProperties():
    # Every calendar provider seems to force strings for extended properties
    scheduled_event_id : str
    message_id : str
    
    def __init__(self, *, scheduled_event_id: int, message_id: int) -> None:
        self.scheduled_event_id = str(scheduled_event_id)
        self.message_id = str(message_id)