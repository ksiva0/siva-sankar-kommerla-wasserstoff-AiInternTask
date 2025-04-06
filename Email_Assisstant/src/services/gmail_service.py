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

    # ... (rest of your GmailService code)
