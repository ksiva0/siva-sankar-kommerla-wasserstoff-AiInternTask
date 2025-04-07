# Email_Assistant/src/services/gmail_service.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import base64
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class GmailService:
    def __init__(self, creds: Credentials):
        if not creds or not creds.valid:
            logging.error("Invalid or missing Gmail API credentials.")
            raise ValueError("Gmail credentials are required and must be valid.")

        self.creds = creds
        self.service = build("gmail", "v1", credentials=self.creds)

    def list_messages(self, label_ids=['INBOX'], max_results=10):
        try:
            response = self.service.users().messages().list(userId='me', labelIds=label_ids, maxResults=max_results).execute()
            return response.get('messages', [])
        except HttpError as error:
            logging.error(f"Error listing messages: {error}")
            return []

    def get_message(self, msg_id):
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            return message
        except HttpError as error:
            logging.error(f"Error getting message {msg_id}: {error}")
            return None

    def get_message_body(self, message):
        try:
            payload = message.get('payload', {})
            parts = payload.get('parts', [])

            if parts:
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            return base64.urlsafe_b64decode(data).decode()
            else:
                body = payload.get('body', {}).get('data')
                if body:
                    return base64.urlsafe_b64decode(body).decode()
        except Exception as e:
            logging.error(f"Error decoding message body: {e}")
        return ""

    def fetch_and_parse_emails(self, max_results=10):
        parsed_emails = []
        messages = self.list_messages(max_results=max_results)
        for msg in messages:
            msg_id = msg.get('id')
            full_msg = self.get_message(msg_id)
            if full_msg:
                parsed_emails.append({
                    'id': full_msg['id'],
                    'threadId': full_msg.get('threadId'),
                    'snippet': full_msg.get('snippet'),
                    'body': self.get_message_body(full_msg),
                    'headers': full_msg['payload'].get('headers', [])
                })
        return parsed_emails
