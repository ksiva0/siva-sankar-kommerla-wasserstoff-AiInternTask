# src/test_oauth.py

import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os

def authenticate_gmail():
    creds = None
    if 'token.pickle' in os.listdir():
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        client_config = {
            "web": {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }

        flow = InstalledAppFlow.from_client_config(
            client_config,
            ['https://www.googleapis.com/auth/gmail.readonly']
        )

        try:
            creds = flow.run_local_server(port=0)
        except Exception as e:
            st.write(f"Failed to run local server: {e}")
            authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
            st.write(f"Please visit this URL: {authorization_url}")
            authorization_response = st.text_input("Enter the authorization response URL:")
            if authorization_response:
                flow.fetch_token(authorization_response=authorization_response)
                creds = flow.credentials

        if creds:
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            st.success("Authentication successful!")
            return creds
        else:
            st.error("Authentication failed.")
            return None

def main():
    st.title("OAuth 2.0 Test")
    if st.button("Authenticate with Gmail"):
        authenticate_gmail()

if __name__ == "__main__":
    main()
