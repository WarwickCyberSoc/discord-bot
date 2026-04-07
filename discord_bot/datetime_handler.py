from datetime import datetime

import dateparser
from dateparser.conf import Settings

SETTINGS = {
    'PREFER_DATES_FROM'        : 'future',
    'TIMEZONE'                 : 'Europe/London',
    'RETURN_AS_TIMEZONE_AWARE' : True,
    'DATE_ORDER'               : 'DMY', # Security feature: Americans are barred from using this bot :P
}

def parse_to_timestamp(text: str) -> float:
    dt = dateparser.parse(text, settings=SETTINGS)
    if not dt:
        raise ValueError(f"Could not parse date string: {text!r}")
    return dt.timestamp()

def timestamp_to_human(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%d/%m/%Y %H:%M:%S')