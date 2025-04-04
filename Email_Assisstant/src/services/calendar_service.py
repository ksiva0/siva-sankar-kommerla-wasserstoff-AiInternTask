# src/services/calendar_service.py
import os
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.service = self.authenticate_calendar()

    def authenticate_calendar(self):
        credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        if not os.path.exists(credentials_path):
            raise FileNotFoundError("Google Calendar credentials file not found. Ensure the path is correct.")
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        return build('calendar', 'v3', credentials=creds)

    def create_event(self, summary, start_time, end_time, description="", attendees=[]):
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
            'attendees': [{'email': email} for email in attendees] if attendees else [],
        }
        event_result = self.service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event_result.get('htmlLink')}")
        return event_result

    def get_events(self, max_results=10):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
