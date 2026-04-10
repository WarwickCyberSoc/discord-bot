from abc import ABC, abstractmethod

from google.oauth2 import service_account
from googleapiclient.discovery import build

class CalendarProvider(ABC):
    @abstractmethod
    def authenticate(self):
        pass
    
    @abstractmethod
    def create_event(self, details: object) -> str:
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
            
    def create_event(self, details: object) -> str:
        event = self.service.events().insert(calendarId=self.id, body=details).execute()
        return event.get('id')