# src/services/gmail_service.py

import os
import pickle
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import logging


class GmailService:
    def __init__(self, credentials=None):
        self.service = None
        self.logger = logging.getLogger(__name__)
        self.authenticate(credentials)

    def authenticate(self, credentials=None):
        creds = credentials

        if not creds:
            # Load token from file if available
            if 'token.pickle' in os.listdir():
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)

            # Refresh token or get new one
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Manual auth flow for Streamlit (console/cloud)
                    client_config = {
                        "installed": {
                            "client_id": st.secrets["google_oauth"]["client_id"],
                            "client_secret": st.secrets["google_oauth"]["client_secret"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
                        }
                    }

                    flow = InstalledAppFlow.from_client_config(
                        client_config,
                        ['https://www.googleapis.com/auth/gmail.readonly',
                         'https://www.googleapis.com/auth/gmail.send']
                    )

                    # Display authorization URL
                    auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
                    st.write("### 🔐 Step 1: Authorize Gmail Access")
                    st.write(f"👉 [Click here to authorize]({auth_url}) and paste the code below.")

                    # User inputs code manually
                    code = st.text_input("Step 2: Paste the authorization code here")

                    if code:
                        try:
                            flow.fetch_token(code=code)
                            creds = flow.credentials
                        except Exception as e:
                            st.error(f"Failed to fetch token: {e}")
                            return

                # Save token for next time
                if creds:
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)

        # Initialize Gmail API service
        if creds:
            self.service = build('gmail', 'v1', credentials=creds)
        else:
            self.logger.error("❌ No valid credentials found for Gmail API.")

    def list_messages(self, user_id='me', label_ids=['INBOX'], max_results=10):
        try:
            results = self.service.users().messages().list(
                userId=user_id, labelIds=label_ids, maxResults=max_results).execute()
            return results.get('messages', [])
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            st.error(f"An error occurred: {e}")
            return []

    def get_message(self, message_id, user_id='me', format='full'):
        if not self.service:
            st.warning("⚠️ Gmail service not initialized.")
            return None
        try:
            return self.service.users().messages().get(userId=user_id, id=message_id, format=format).execute()
        except Exception as e:
            st.error(f"An error occurred while getting message: {e}")
            self.logger.error(f"An error occurred while getting message: {e}")
            return None

    def get_email_data(self, message):
        headers = message['payload']['headers']
        sender = next((h['value'] for h in headers if h['name'] == 'From'), None)
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), None)
        date = next((h['value'] for h in headers if h['name'] == 'Date'), None)
        body = self.get_email_body(message['payload'])

        return {
            'sender': sender,
            'subject': subject,
            'date': date,
            'body': body
        }

    def get_email_body(self, payload):
        if 'parts' in payload:
            parts = payload['parts']
            text_parts = [self.get_email_body(p) for p in parts if p['mimeType'] == 'text/plain']
            html_parts = [self.get_email_body(p) for p in parts if p['mimeType'] == 'text/html']
            return '\n'.join(text_parts) or '\n'.join(html_parts)
        elif 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(payload['body']['data'].encode('ascii')).decode('utf-8', errors='ignore')
        return ''

    def send_message(self, user_id='me', message_body='', to='', subject=''):
        if not self.service:
            st.warning("⚠️ Gmail service not initialized.")
            return

        try:
            message = MIMEText(message_body)
            message['to'] = to
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_message = self.service.users().messages().send(userId=user_id, body={'raw': raw_message}).execute()
            self.logger.info(f"✅ Email sent: {send_message['id']}")
            return send_message
        except Exception as e:
            st.error(f"An error occurred while sending message: {e}")
            self.logger.error(f"An error occurred while sending message: {e}")
            return None
