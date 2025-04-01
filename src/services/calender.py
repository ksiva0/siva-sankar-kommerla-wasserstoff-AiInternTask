from googleapiclient.discovery import build  

def create_calendar_event(service, summary, start_time, end_time):  
    event = {  
        'summary': summary,  
        'start': {  
            'dateTime': start_time,  
            'timeZone': 'America/Los_Angeles',  
        },  
        'end': {  
            'dateTime': end_time,  
            'timeZone': 'America/Los_Angeles',  
        },  
    }  
    event = service.events().insert(calendarId='primary', body=event).execute()  
    return event.get('htmlLink')  
