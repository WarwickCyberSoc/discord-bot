from datetime import datetime

import dateparser
from dateparser.conf import Settings

SETTINGS = {
    'PREFER_DATES_FROM'        : 'future',
    'TIMEZONE'                 : 'Europe/London',
    'RETURN_AS_TIMEZONE_AWARE' : True,
    'DATE_ORDER'               : 'DMY', # Security feature: Americans are barred from using this bot :P
}

def parse_datetime(text: str) -> datetime:
    dt = dateparser.parse(text, settings=SETTINGS)
    if not dt:
        raise ValueError(f"Could not parse date string: {text!r}")
    if dt.timestamp() < datetime.now().timestamp():
        raise ValueError(f"Cannot create event in the past")
    return dt

def datetime_format(dt: datetime) -> str:
    return dt.strftime('%d/%m/%Y %H:%M:%S')