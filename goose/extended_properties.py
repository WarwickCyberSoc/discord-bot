class ExtendedProperties():
    # Every calendar provider seems to force strings for extended properties
    scheduled_event_id : str
    message_id : str
    event_type : str
    
    def __init__(self, *, scheduled_event_id: int, message_id: int,
                 event_type: str = 'academic') -> None:
        self.scheduled_event_id = str(scheduled_event_id)
        self.message_id = str(message_id)
        self.event_type = event_type