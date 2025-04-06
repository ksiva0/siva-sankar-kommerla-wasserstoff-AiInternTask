import os
import pickle
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging
import streamlit as st 

class GmailService:
    def __init__(self, credentials):
        self.logger = logging.getLogger(__name__)
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Use credentials from Streamlit Secrets
                client_config = st.secrets["credentials"]  # Get credentials from secrets
                flow = InstalledAppFlow.from_client_config(
                    client_config, ['https://www.googleapis.com/auth/gmail.readonly'])  # Adjust scopes as needed
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def get_emails(self, num_emails=5):
        try:
            results = self.service.users().messages().list(userId='me', maxResults=num_emails).execute()
            messages = results.get('messages', [])
            emails = []
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg['payload']
                headers = payload['headers']
                body = ""
                if 'parts' in payload:
                  for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                      body = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')).decode('utf-8')
                      break
                else:
                  body = base64.urlsafe_b64decode(payload['body']['data'].encode('ASCII')).decode('utf-8')

                sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
                emails.append({
                    'id': message['id'],
                    'sender': sender,
                    'subject': subject,
                    'body': body
                })
            return emails
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return []
