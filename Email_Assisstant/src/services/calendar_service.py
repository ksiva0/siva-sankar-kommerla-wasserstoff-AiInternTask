# src/services/calendar_service.py

import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.service = self.authenticate_calendar()

    def authenticate_calendar(self):
        try:
            calendar_secrets = dict(st.secrets["calendar"])
            creds = service_account.Credentials.from_service_account_info(
                calendar_secrets, scopes=SCOPES
            )
            return build('calendar', 'v3', credentials=creds)
        except Exception as e:
            st.error("❌ Failed to authenticate with Google Calendar API.")
            raise RuntimeError(f"Google Calendar authentication error: {e}")

    def create_event(self, summary, start_time, end_time, description="", attendees=[]):
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
            'attendees': [{'email': email} for email in attendees] if attendees else [],
        }
        try:
            event_result = self.service.events().insert(calendarId='primary', body=event).execute()
            st.success(f"📅 Event created: {event_result.get('htmlLink')}")
            return event_result
        except Exception as e:
            st.error("⚠️ Failed to create event.")
            raise RuntimeError(f"Event creation error: {e}")

    def get_events(self, max_results=10):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except Exception as e:
            st.error("⚠️ Failed to fetch upcoming events.")
            raise RuntimeError(f"Get events error: {e}")
