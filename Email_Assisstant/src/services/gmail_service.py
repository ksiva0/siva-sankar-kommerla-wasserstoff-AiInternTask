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
    def __init__(self):
        self.service = None
        self.logger = logging.getLogger(__name__)
        self.authenticate()

    def authenticate(self):
        creds = None
        if 'token.pickle' in os.listdir():
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                redirect_uri = st.secrets["google_oauth"]["redirect_uri"]
                print(f"Redirect URI being used: {redirect_uri}") # Debugging line.
                client_config = {
                    "web": {
                        "client_id": st.secrets["google_oauth"]["client_id"],
                        "client_secret": st.secrets["google_oauth"]["client_secret"],
                        "redirect_uris": [redirect_uri],
                        "auth_uri": st.secrets["google_oauth"].get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                        "token_uri": st.secrets["google_oauth"].get("token_uri", "https://oauth2.googleapis.com/token")
                    }
                }

                flow = InstalledAppFlow.from_client_config(
                    client_config,
                    ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
                )

                try:
                    creds = flow.run_local_server(port=0)  # Attempt to run in headed mode
                except Exception as e:
                    self.logger.warning(f"Failed to run local server: {e}. Falling back to manual authorization.")
                    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
                    email_url = "https://mail.google.com/mail/u/0/"
                    st.write(f"Please visit this URL: {authorization_url}")
                    st.write(f"Once you have authorized, paste the resulting URL here.")
                    st.write(f"This application is requesting access to your email at: {email_url}")
                    authorization_response = st.text_input("Enter the authorization response URL:")
                    if authorization_response:
                        try:
                            flow.fetch_token(authorization_response=authorization_response)
                            creds = flow.credentials
                        except Exception as fetch_error:
                            st.error(f"Failed to fetch token: {fetch_error}")
                            return

                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def list_messages(self, user_id='me', label_ids=['INBOX'], max_results=10):
        try:
            results = self.service.users().messages().list(userId=user_id, labelIds=label_ids, maxResults=max_results).execute()
            messages = results.get('messages', [])
            return messages
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            st.error(f"An error occurred: {e}")
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
