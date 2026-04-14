from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union

import dismoji
from google.oauth2 import service_account
from googleapiclient.discovery import HttpError, build

from extended_properties import ExtendedProperties
from society_event import SocietyEvent

class CalendarProvider(ABC):
    @abstractmethod
    def authenticate(self):
        pass
    
    @abstractmethod
    def do_event(self, event: SocietyEvent, data: ExtendedProperties) -> str:
        pass
    
    @abstractmethod
    def get_event(self, id: str) -> Optional[ExtendedProperties]:
        pass
    
    @abstractmethod
    def delete_event(self, id: str) -> Optional[ExtendedProperties]:
        pass

class GoogleCalendar(CalendarProvider):
    SCOPES = [ "https://www.googleapis.com/auth/calendar" ]
    SERVICE_ACCOUNT_FILE = "google_credentials.json"
    
    def __init__(self, calendar_id: str) -> None:
        self.id = calendar_id
        self.service = None
    
    def authenticate(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES
        )
        self.service = build("calendar", "v3", credentials=credentials)
            
    def do_event(self, event: SocietyEvent, data: ExtendedProperties) -> str:
        details = {
            'summary': dismoji.emojize(event.title),
            'description': dismoji.emojize(event.short_text),
            'start': self._google_datetime(event.start),
            'extendedProperties': {
                'private': data.__dict__
            }
        }
        
        if not event.has_physical_location():
            details['location'] = 'Discord Server'
        else:
            details['location'] = dismoji.emojize(event.location)
            
        if event.end:
            details['end'] = self._google_datetime(event.end)
        else:
            details['end'] = self._google_datetime(event.start.replace(hour=23, minute=59))
        
        if event.id:
            calendar_event = self.service.events().update(calendarId=self.id, eventId=event.id, body=details).execute()
        else:
            calendar_event = self.service.events().insert(calendarId=self.id, body=details).execute()
        return calendar_event['id']
    
    @staticmethod
    def _google_datetime(dt: datetime):
        return {
            'dateTime': dt.isoformat(timespec='seconds'),
            'timeZone': 'Europe/London'
        }
    
    def get_event(self, id: str) -> Optional[ExtendedProperties]:
        try:
            event = self.service.events().get(calendarId=self.id, eventId=id).execute()
            return ExtendedProperties(**event['extendedProperties']['private'])
        except HttpError as error:
            if error.resp.status in [404, 410]:
                return None
            else:
                raise error
            
    def delete_event(self, id: str) -> Optional[ExtendedProperties]:
        props = self.get_event(id)
        if not props:
            return None
        
        try:
            self.service.events().delete(calendarId=self.id, eventId=id).execute()
            return props
        except HttpError as error:
            if error.resp.status in [404, 410]:
                return None 
            raise error