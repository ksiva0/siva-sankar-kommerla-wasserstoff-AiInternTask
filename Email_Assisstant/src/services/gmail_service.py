# src/services/gmail_service.py

import os
import pickle
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import logging
import streamlit as st
from google_auth_oauthlib.flow import Flow
import json
import sys

class GmailService:
    def __init__(self, credentials=None):
        self.logger = logging.getLogger(__name__)
        self.creds = credentials if credentials else self._authenticate()
        if self.creds and self.creds.valid:
            try:
                self.service = build('gmail', 'v1', credentials=self.creds)
            except Exception as e:
                self.logger.error(f"Failed to initialize Gmail service: {e}")
                st.error("Failed to initialize Gmail service.")
                self.service = None
        else:
            self.logger.warning("No valid credentials available.")
            self.service = None

    def _load_client_config(self):
        try:
            config = {
                "web": {
                    "client_id": st.secrets["google_oauth"]["client_id"],
                    "client_secret": st.secrets["google_oauth"]["client_secret"],
                    "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]],
                    "auth_uri": st.secrets["google_oauth"].get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                    "token_uri": st.secrets["google_oauth"].get("token_uri", "https://oauth2.googleapis.com/token")
                }
            }
            return config
        except Exception as e:
            self.logger.error(f"Error loading google_oauth secret: {e}")
            st.error("Error loading google_oauth secret. Please check your Streamlit Secrets configuration. Expected keys: client_id, client_secret, redirect_uri, auth_uri, token_uri.")
            sys.exit(1)

    def _authenticate(self):
        creds = None
        if 'token' in st.session_state:
            try:
                creds = Credentials.from_authorized_user_info(json.loads(st.session_state['token']))
                self.logger.info("Loaded credentials from session state.")
            except Exception as e:
                self.logger.error(f"Error loading credentials from session state: {e}")
    
        if not creds or not creds.valid:
            self.logger.info("Credentials are missing or invalid.")
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("Credentials refreshed successfully.")
                except Exception as e:
                    self.logger.error(f"Failed to refresh token: {e}")
                    st.error("🔁 Failed to refresh credentials. Please re-authorize.")
                    return None
            else:
                code = st.query_params.get("code")
                if code:
                    self.logger.info(f"Received auth code: {code}")
                    try:
                        client_config = self._load_client_config()
                        flow = Flow.from_client_config(
                            client_config,
                            scopes=[
                                'https://www.googleapis.com/auth/gmail.readonly',
                                'https://www.googleapis.com/auth/gmail.send'
                            ],
                            redirect_uri=client_config["web"]["redirect_uris"][0],
                        )
                        flow.fetch_token(code=code)
                        creds = flow.credentials
                        st.session_state['token'] = creds.to_json()
                        self.logger.info("Fetched new credentials from code.")
                        st.query_params.clear()
                    except Exception as e:
                        self.logger.error(f"Error fetching token from code: {e}")
                        st.error("🔑 Failed to fetch token. Please re-authorize.")
                        return None
                else:
                    self.logger.info("No code found. Asking for authorization.")
                    try:
                        client_config = self._load_client_config()
                        flow = Flow.from_client_config(
                            client_config,
                            scopes=[
                                'https://www.googleapis.com/auth/gmail.readonly',
                                'https://www.googleapis.com/auth/gmail.send'
                            ],
                            redirect_uri=client_config["web"]["redirect_uris"][0],
                        )
                        authorization_url, _ = flow.authorization_url(
                            access_type='offline',
                            include_granted_scopes='true'
                        )
                        st.markdown(f'📧 [Click here to authorize Gmail access]({authorization_url})')
                        return None
                    except Exception as e:
                        self.logger.error(f"Error generating auth URL: {e}")
                        st.error("❌ Failed to generate auth URL.")
                        return None
        return creds


    def get_emails(self, num_emails=5):
        if self.service is None:
            st.error("Gmail service not initialized. Authentication failed.")
            return []

        try:
            results = self.service.users().messages().list(userId='me', maxResults=num_emails).execute()
            messages = results.get('messages', [])
            emails = []
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])
                body = ""
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')).decode('utf-8')
                            break
                elif 'body' in payload and 'data' in payload['body']:
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
            st.error("Failed to fetch emails from Gmail.")
            return []
