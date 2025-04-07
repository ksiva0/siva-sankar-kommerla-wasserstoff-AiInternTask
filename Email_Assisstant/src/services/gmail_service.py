# Email_Assistant/src/services/gmail_service.py

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import base64
import logging
import sys

# Set up logging to stdout (helpful in Vercel or cloud deployments)
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
            messages = response.get('messages', [])
            return messages
        except HttpError as error:
            logging.error(f"An error occurred while listing messages: {error}")
            return []

    def get_message(self, msg_id):
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            return message
        except HttpError as error:
            if error.resp.status == 404:
                logging.error(f"Message with ID {msg_id} not found. It may have been deleted or is invalid.")
            else:
                logging.error(f"An error occurred while getting message {msg_id}: {error}")
            return None

    def get_message_body(self, message):
        try:
            payload = message.get('payload', {})
            parts = payload.get('parts', [])
            body = ""

            if parts:
                for part in parts:
                    mime_type = part.get('mimeType')
                    data = part.get('body', {}).get('data')

                    if mime_type == 'text/plain' and data:
                        body = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                        break  # Get the first text/plain part

                    elif mime_type == 'text/html' and data:
                        body = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                        break  # Get the first text/html part

            elif payload.get('body') and payload.get('body').get('data'):
                data = payload['body']['data']
                mime_type = payload.get('mimeType')

                if mime_type == 'text/plain' or mime_type == 'text/html':
                    body = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')

            return body

        except Exception as e:
            logging.error(f"Error decoding message body: {e}")
            return ""

    def fetch_and_parse_emails(self, max_results=10):
        parsed_emails = []
        messages = self.list_messages(max_results=max_results)
        if messages:
            for msg in messages:
                msg_id = msg.get('id')
                if not msg_id:
                    logging.warning("Skipping message without ID.")
                    continue

                full_msg = self.get_message(msg_id)
                if full_msg:
                    email_data = {
                        'id': full_msg['id'],
                        'threadId': full_msg.get('threadId'),
                        'snippet': full_msg.get('snippet'),
                        'body': self.get_message_body(full_msg),
                        'headers': full_msg['payload'].get('headers', [])
                    }
                    parsed_emails.append(email_data)
        return parsed_emails
