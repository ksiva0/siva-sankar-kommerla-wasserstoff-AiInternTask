from google.oauth2.credentials import Credentials  
from google_auth_oauthlib.flow import InstalledAppFlow  
from googleapiclient.discovery import build  
import os  

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']  

def authenticate_gmail():  
    creds = None  
    if os.path.exists('token.json'):  
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)  
    if not creds or not creds.valid:  
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)  
        creds = flow.run_local_server(port=0)  
        with open('token.json', 'w') as token:  
            token.write(creds.to_json())  
    return creds  

async def fetch_emails():  
    creds = authenticate_gmail()  
    service = build('gmail', 'v1', credentials=creds)  
    results = service.users().messages().list(userId='me', maxResults=10).execute()  
    messages = results.get('messages', [])  
    if not messages:  
        return []  
    # Fetch messages details  
    emails = []  
    for message in messages:  
        msg = service.users().messages().get(userId='me', id=message['id']).execute()  
        emails.append(msg)  
    return emails  

async def reply_to_email(email_id: str, reply_body: str):  
    # Implement reply functionality here  
    pass  
