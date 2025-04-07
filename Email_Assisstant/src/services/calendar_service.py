from googleapiclient.discovery import build  
from google.oauth2.credentials import Credentials  
import os  

def authenticate_calendar():  
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)  
    return build('calendar', 'v3', credentials=creds)  

async def create_event(event_details):  
    service = authenticate_calendar()  
    event = {  
        'summary': event_details['summary'],  
        'start': {  
            'dateTime': event_details['start'],  
            'timeZone': 'America/New_York',  
        },  
        'end': {  
            'dateTime': event_details['end'],  
            'timeZone': 'America/New_York',  
        },  
    }  
    service.events().insert(calendarId='primary', body=event).execute()  
