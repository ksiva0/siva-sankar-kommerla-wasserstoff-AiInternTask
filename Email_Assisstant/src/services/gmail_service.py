import os
import pickle
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import logging
import streamlit as st

class GmailService:
    def __init__(self, credentials):
        self.logger = logging.getLogger(__name__)
        self.creds = self._authenticate()
        if self.creds: #only build if auth was successful.
            self.service = build('gmail', 'v1', credentials=self.creds)
        else:
            self.service = None

    def _authenticate(self):
        creds = None
        if 'token' in st.session_state:
            creds = Credentials.from_authorized_user_info(st.session_state['token'])

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                code = st.query_params.get("code")
                if code:
                    try:
                        import google.auth.transport.requests
                        from google_auth_oauthlib.flow import Flow #import here
                        flow = Flow.from_client_config(
                            st.secrets["google_oauth"],
                            scopes=['https://www.googleapis.com/auth/gmail.readonly'],
                            redirect_uri=st.secrets["google_oauth"]["redirect_uri"]
                        )
                        flow.fetch_token(code=code) #code is already a list like object when using st.query_params
                        creds = flow.credentials
                        st.session_state['token'] = creds.to_json() # store token in session state.
                        st.query_params.clear() #clear query parameters
                    except Exception as e:
                        st.error(f"Error authenticating: {e}")
                        return None
                else:
                    try:
                        import google_auth_oauthlib.flow #import here
                        flow = google_auth_oauthlib.flow.Flow.from_client_config(
                            st.secrets["google_oauth"],
                            scopes=['https://www.googleapis.com/auth/gmail.readonly'],
                            redirect_uri=st.secrets["google_oauth"]["redirect_uri"]
                        )
                        authorization_url, state = flow.authorization_url(
                            access_type='offline',
                            include_granted_scopes='true'
                        )
                        st.markdown(f'<a href="{authorization_url}">Authorize</a>', unsafe_allow_html=True)
                        return None
                    except Exception as e:
                        st.error(f"Error generating auth url: {e}")
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
                payload = msg['payload']
                headers = payload['headers']
                body = ""
                if 'parts' in payload:
                  for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                      body = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')).decode('utf-8')
                      break
                else:
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
            return []
