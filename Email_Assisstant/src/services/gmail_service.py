# Email_Assistant/src/services/gmail_service.py

import base64
import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("gmail", "v1", credentials=creds)
    return service


def fetch_emails():
    service = get_service()
    results = service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=10).execute()
    messages = results.get("messages", [])
    parsed_emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")
        snippet = msg_data.get("snippet", "")
        parsed_emails.append({"id": msg["id"], "subject": subject, "sender": sender, "snippet": snippet})

    return parsed_emails
