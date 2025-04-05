# src/services/gmail_service.py
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/userinfo.email']
REDIRECT_URI = "http://localhost:8501"

class GmailService:
    def __init__(self):
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
        )
        return build('gmail', 'v1', credentials=creds)

    def fetch_emails(self):
        results = self.service.users().messages().list(userId='me', maxResults=10).execute()
        return results.get('messages', [])

    def get_email_content(self, msg_id):
        msg = self.service.users().messages().get(userId='me', id=msg_id).execute()
        payload = msg.get('payload', {})
        parts = payload.get('parts', [])
        body_data = None

        for part in parts:
            if 'body' in part and 'data' in part['body']:
                body_data = part['body']['data']
                break

        msg_str = base64.urlsafe_b64decode(body_data).decode() if body_data else "No content found"
        return {
            "id": msg_id,
            "snippet": msg['snippet'],
            "data": msg_str
        }

    def send_email(self, to, subject, message_text):
        from email.mime.text import MIMEText
        message = MIMEText(message_text)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        self.service.users().messages().send(userId='me', body={'raw': raw}).execute()
