import os  
import pickle  
import base64  
from google.auth.transport.requests import Request  
from google.oauth2.credentials import Credentials  
from google_auth_oauthlib.flow import InstalledAppFlow  
from googleapiclient.discovery import build  

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']  

def authenticate_gmail():  
    creds = None  
    if os.path.exists('token.pickle'):  
        with open('token.pickle', 'rb') as token:  
            creds = pickle.load(token)  
    if not creds or not creds.valid:  
        if creds and creds.expired and creds.refresh_token:  
            creds.refresh(Request())  
        else:  
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)  
            creds = flow.run_local_server(port=0)  
        with open('token.pickle', 'wb') as token:  
            pickle.dump(creds, token)  
    return creds  

def fetch_emails(service, user_id='me'):  
    results = service.users().messages().list(userId=user_id, labelIds=["INBOX"], maxResults=10).execute()  
    emails = []  
    for msg in results.get('messages', []):  
        msg_data = service.users().messages().get(userId=user_id, id=msg['id']).execute()  
        email_data = msg_data['payload']['headers']  
        subject = next(header['value'] for header in email_data if header['name'] == 'Subject')  
        from_ = next(header['value'] for header in email_data if header['name'] == 'From')  
        body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode('utf-8')  
        emails.append({'subject': subject, 'from': from_, 'body': body})  
    return emails
