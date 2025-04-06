# src/services/gmail_service.py
import os
import base64
import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self.service = None
        if not use_mock:
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = Flow.from_client_secrets_file(
                        'credentials.json',
                        scopes=SCOPES,
                        redirect_uri='http://localhost:8501'
                    )
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    st.write(f"Please authorize access: [Click here]({auth_url})")
                    return

            self.service = build('gmail', 'v1', credentials=creds)

    def fetch_emails(self, max_results=10):
        if self.use_mock:
            return [
                {"id": "mock1"},
                {"id": "mock2"},
            ]
        if not self.service:
            raise RuntimeError("Gmail API service is not initialized.")
        
        results = self.service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=""  # No filter = fetch all emails, not just unread
        ).execute()

        messages = results.get('messages', [])
        return messages

    def get_email_content(self, msg_id):
        message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        headers = message['payload'].get('headers', [])
        header_dict = {h['name']: h['value'] for h in headers}

        snippet = message.get('snippet', '')
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

        return {
            "from": header_dict.get("From"),
            "to": header_dict.get("To"),
            "subject": header_dict.get("Subject"),
            "snippet": snippet,
            "data": body,
            "timestamp": int(message.get("internalDate", 0)) / 1000
        }

    def send_email(self, to, subject, message_text):
        if self.use_mock:
            print(f"📤 Mock email sent to {to} with subject '{subject}'")
            return
        from email.mime.text import MIMEText
        message = MIMEText(message_text)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return self.service.users().messages().send(userId='me', body={'raw': raw}).execute()
