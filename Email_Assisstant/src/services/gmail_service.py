# src/services/gmail_service.py

import os
import pickle
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

class GmailService:
    def __init__(self):
        self.service = None
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

            # Add Google OAuth client secrets from Streamlit secrets
            oauth_info = {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]],
                "auth_uri": st.secrets["google_oauth"].get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                "token_uri": st.secrets["google_oauth"].get("token_uri", "https://oauth2.googleapis.com/token")
            }

            creds = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=[
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/gmail.send'
                ]
            )

            self.service = build('gmail', 'v1', credentials=creds)
            st.session_state["gmail_authenticated"] = True

        except Exception as e:
            st.error(f"Gmail service authentication failed: {e}")
            self.service = None

    def get_service(self):
        return self.service

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
            return []

    def get_message(self, message_id, user_id='me'):
        if not self.service:
            return None
        try:
            message = self.service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
            return message
        except Exception as e:
            st.error(f"An error occurred while getting message: {e}")
            return None
