# src/services/gmail_service.py

import base64
import logging
import streamlit as st
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from typing import List, Dict, Optional

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self.service = None
        if not self.use_mock:
            self.service = self._authenticate()
            if self.service is None:
                logging.error("❌ Gmail service not initialized. Please check your credentials.")

    def _authenticate(self):
        try:
            # Debug: Check if credentials are available
            if "credentials" not in st.secrets:
                logging.error("❌ 'credentials' not found in Streamlit secrets.")
                return None
    
            creds_data = st.secrets["credentials"]
            logging.info(f"✅ Credentials keys loaded: {list(creds_data.keys())}")
    
            creds = Credentials.from_authorized_user_info(
                info=creds_data,
                scopes=SCOPES
            )
    
            service = build('gmail', 'v1', credentials=creds)
            logging.info("✅ Gmail service initialized successfully.")
            return service
    
        except Exception as e:
            logging.error(f"❌ Failed to authenticate with Gmail: {e}")
            return None

    def fetch_emails(self, max_results: int = 10) -> List[Dict]:
        """Fetch email metadata (IDs) from the user's inbox."""
        if self.use_mock:
            return [{"id": "mock1"}, {"id": "mock2"}]

        if not self.service:
            raise RuntimeError("Gmail service not initialized")

        try:
            messages = []
            response = self.service.users().messages().list(userId='me', maxResults=max_results).execute()
            messages.extend(response.get('messages', []))

            while 'nextPageToken' in response and len(messages) < max_results:
                response = self.service.users().messages().list(
                    userId='me',
                    maxResults=max_results - len(messages),
                    pageToken=response['nextPageToken']
                ).execute()
                messages.extend(response.get('messages', []))

            return messages

        except HttpError as error:
            logging.error(f"Gmail API error during fetch_emails: {error}")
            return []

    def get_email_content(self, msg_id: str) -> Dict:
        """Retrieve full content of an email by message ID."""
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

            def extract_plain_text(parts):
                for part in parts:
                    if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    if 'parts' in part:
                        result = extract_plain_text(part['parts'])
                        if result:
                            return result
                return ''

            payload = message.get('payload', {})
            if 'parts' in payload:
                body = extract_plain_text(payload['parts'])
            elif 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')

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

    def send_email(self, to: str, subject: str, message_text: str) -> Optional[Dict]:
        """Send an email via the Gmail API."""
        if self.use_mock:
            print(f"📤 Mock email sent to {to} with subject '{subject}'")
            return {"status": "mock", "to": to, "subject": subject}

        if not self.service:
            raise RuntimeError("Gmail service not initialized")

        try:
            message = MIMEText(message_text)
            message['to'] = to
            message['subject'] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            return self.service.users().messages().send(userId='me', body={'raw': raw}).execute()

        except HttpError as error:
            logging.error(f"Error sending email to {to}: {error}")
            return None
