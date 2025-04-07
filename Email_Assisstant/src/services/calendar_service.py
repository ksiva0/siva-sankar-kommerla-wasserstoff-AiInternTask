# Email_Assistant/src/services/calendar_service.py

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("calendar", "v3", credentials=creds)


def schedule_event(event_info):
    service = get_calendar_service()
    event = {
        'summary': event_info['title'],
        'start': {'dateTime': event_info['start'], 'timeZone': 'UTC'},
        'end': {'dateTime': event_info['end'], 'timeZone': 'UTC'}
    }
    service.events().insert(calendarId='primary', body=event).execute()
