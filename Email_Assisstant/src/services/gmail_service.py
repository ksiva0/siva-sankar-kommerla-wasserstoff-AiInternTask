# src/services/gmail_service.py
import os
import base64
import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        if not self.use_mock:
            self.creds = self.authenticate()
            self.service = build('gmail', 'v1', credentials=self.creds)

    def authenticate(self):
        if 'credentials' in st.session_state:
            return st.session_state['credentials']

        
        client_config = {
        "web": {
            "client_id": st.secrets["google_oauth"]["client_id"],
            "client_secret": st.secrets["google_oauth"]["client_secret"],
            "redirect_uri": [st.secrets["google_oauth"]["redirect_uri"]],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
                }
            }

        flow = Flow.from_client_config(
                                    client_config,
                                    scopes=SCOPES,
                                    redirect_uri=st.secrets["google_oauth"]["redirect_uri"]
                                    )

        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"[Authorize Gmail Access]({auth_url})")

        if "code" in st.query_params:
            flow.fetch_token(code=st.query_params["code"])
            creds = flow.credentials
            st.session_state['credentials'] = creds
            return creds

        st.stop()

    def fetch_emails(self, max_results=10):
        # Fetch all messages (not just unread)
        result = self.service.users().messages().list(
            userId='me', maxResults=max_results, q=""
        ).execute()
        messages = result.get('messages', [])
        return messages

    def get_email_content(self, msg_id):
        if self.use_mock:
            return {"snippet": "Mock Email", "data": "Mock body content for testing"}
        message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        snippet = message['snippet']
        data = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8') if 'data' in message['payload']['body'] else ""
        return {"snippet": snippet, "data": data}
        
    def send_email(self, to, subject, message_text):
        if self.use_mock:
            print(f"📤 Mock email sent to {to} with subject '{subject}'")
            return
        from email.mime.text import MIMEText
        message = MIMEText(message_text)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return self.service.users().messages().send(userId='me', body={'raw': raw}).execute()
