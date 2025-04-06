# src/services/gmail_service.py

import os
import pickle
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import base64
import email
from email.mime.text import MIMEText
import logging

class GmailService:
    def __init__(self, user_email='your_user_email@domain.com'): #change to the user email you need to access
        self.service = None
        self.logger = logging.getLogger(__name__)
        self.user_email = user_email
        self.authenticate()

    def authenticate(self):
        try:
            credentials_info = {
                "type": st.secrets["credentials"]["type"],
                "project_id": st.secrets["credentials"]["project_id"],
                "private_key_id": st.secrets["credentials"]["private_key_id"],
                "private_key": st.secrets["credentials"]["private_key"],
                "client_email": st.secrets["credentials"]["client_email"],
                "client_id": st.secrets["credentials"]["client_id"],
                "auth_uri": st.secrets["credentials"]["auth_uri"],
                "token_uri": st.secrets["credentials"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["credentials"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["credentials"]["client_x509_cert_url"],
                "universe_domain": st.secrets["credentials"]["universe_domain"]
            }

            creds = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=[
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.send'
                ]
            )
            delegated_creds = creds.with_subject(self.user_email)
            self.service = build('gmail', 'v1', credentials=delegated_creds)

            st.session_state["gmail_authenticated"] = True
            self.logger.info("Gmail service authenticated.")

        except Exception as e:
            st.error(f"Gmail service authentication failed: {e}")
            self.logger.error(f"Gmail service authentication failed: {e}")
            self.service = None

    def list_messages(self, user_id='me', label_ids=['INBOX'], max_results=10):
        if not self.service:
            st.warning("Gmail service not initialized. Authentication failed.")
            return []

        try:
            response = self.service.users().messages().list(
                userId=user_id,
                labelIds=label_ids,
                maxResults=max_results
            ).execute()

            messages = response.get('messages', [])
            return messages

        except Exception as e:
            st.error(f"An error occurred while fetching messages: {e}")
            self.logger.error(f"An error occurred while fetching messages: {e}")
            return []

    def get_message(self, message_id, user_id='me', format='full'):
        if not self.service:
            st.warning("Gmail service not initialized. Authentication failed.")
            return None
        try:
            message = self.service.users().messages().get(userId=user_id, id=message_id, format=format).execute()
            return message
        except Exception as e:
            st.error(f"An error occurred while getting message: {e}")
            self.logger.error(f"An error occurred while getting message: {e}")
            return None

    def get_email_data(self, message):
        headers = message['payload']['headers']
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        date = next((header['value'] for header in headers if header['name'] == 'Date'), None)

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
            text_parts = [self.get_email_body(part) for part in parts if part['mimeType'] == 'text/plain']
            html_parts = [self.get_email_body(part) for part in parts if part['mimeType'] == 'text/html']
            return '\n'.join(text_parts) or '\n'.join(html_parts)
        elif 'data' in payload:
            return base64.urlsafe_b64decode(payload['data'].encode('ascii')).decode('utf-8', errors='ignore')
        return ''

    def send_message(self, user_id='me', message_body='', to='', subject=''):
        if not self.service:
            st.warning("Gmail service not initialized. Authentication failed.")
            return

        try:
            message = MIMEText(message_body)
            message['to'] = to
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            send_message = self.service.users().messages().send(userId=user_id, body={'raw': raw_message}).execute()
            self.logger.info(f"Email sent: {send_message['id']}")
            return send_message
        except Exception as e:
            st.error(f"An error occurred while sending message: {e}")
            self.logger.error(f"An error occurred while sending message: {e}")
            return None
