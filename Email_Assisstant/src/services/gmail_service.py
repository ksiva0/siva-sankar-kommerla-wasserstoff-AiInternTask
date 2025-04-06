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
                client_config = {
                    "web": {
                        "client_id": st.secrets["google_oauth"]["client_id"],
                        "client_secret": st.secrets["google_oauth"]["client_secret"],
                        "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]],
                        "auth_uri": st.secrets["google_oauth"].get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                        "token_uri": st.secrets["google_oauth"].get("token_uri", "https://oauth2.googleapis.com/token")
                    }
                }

                flow = InstalledAppFlow.from_client_config(
                    client_config,
                    ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
                )
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        # Verify credentials using service account info. This is a check, not the main auth.
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

            service_account_creds = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=[
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.send'
                ]
            )
            #If the code reaches here, then the credentials are valid.
            self.logger.info("Service Account Credentials are Valid.")

        except Exception as e:
            self.logger.error(f"Service Account Credentials check failed: {e}")
            st.error(f"Service Account Credentials check failed: {e}")

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

    # ... (rest of the code remains the same)
