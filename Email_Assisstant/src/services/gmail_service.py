import base64
import logging
import streamlit as st
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self.service = None
        if not self.use_mock:
            self.service = self._authenticate()

    def _authenticate(self):
        try:
            creds_data = st.secrets["credentials"]
            creds = Credentials.from_authorized_user_info(info=creds_data, scopes=SCOPES)
            service = build('gmail', 'v1', credentials=creds)
            logging.info("✅ Gmail authenticated successfully.")
            return service
        except Exception as e:
            logging.error(f"❌ Failed to authenticate with Gmail: {e}")
            return None

    def fetch_emails(self, max_results=10):
        if self.use_mock:
            return [{"id": "mock1"}, {"id": "mock2"}]

        if not self.service:
            logging.error("❌ Gmail service not initialized. Please check your credentials.")
            return []

        try:
            response = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
            return response.get('messages', [])
        except HttpError as error:
            logging.error(f"Gmail API error during fetch_emails: {error}")
            return []

    def get_email_content(self, msg_id):
        if self.use_mock:
            return {
                "from": "mock@example.com",
                "to": "you@example.com",
                "subject": "Test Subject",
                "snippet": "Snippet here",
                "data": "Body text of the email.",
                "timestamp": 1712390400,
            }

        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            headers = message['payload'].get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}

            snippet = message.get('snippet', '')
            body = ''

            parts = message['payload'].get('parts', [])
            if parts:
                for part in parts:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8', errors='ignore')

            return {
                "from": header_dict.get("From"),
                "to": header_dict.get("To"),
                "subject": header_dict.get("Subject"),
                "snippet": snippet,
                "data": body,
                "timestamp": int(message.get("internalDate", 0)) / 1000
            }

        except HttpError as error:
            logging.error(f"Error fetching email content for {msg_id}: {error}")
            return {}

    def send_email(self, to, subject, message_text):
        if self.use_mock:
            print(f"📤 Mock email sent to {to} with subject '{subject}'")
            return

        if not self.service:
            logging.error("❌ Gmail service not initialized.")
            return

        try:
            message = MIMEText(message_text)
            message['to'] = to
            message['subject'] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            return self.service.users().messages().send(userId='me', body={'raw': raw}).execute()

        except HttpError as error:
            logging.error(f"Error sending email to {to}: {error}")
            return None
