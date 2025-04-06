# src/services/email_controller.py

import os
from openai import OpenAI
from services.gmail_service import GmailService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from services.database_service import DatabaseService
from utils.prompt_engineering import generate_reply_prompt
import streamlit as st
from datetime import datetime

class EmailController:
    def __init__(self, slack_token, use_mock=False):
        self.use_mock = use_mock
        self.gmail_service = GmailService(use_mock=use_mock)
        self.slack_service = SlackService(slack_token)
        self.calendar_service = CalendarService()
        self.openai_api_key = st.secrets["openai"]["OPENAI_API_KEY"]
        self.openai_client = OpenAI(api_key=self.openai_api_key)

    def process_emails(self):
        messages = self.gmail_service.fetch_emails()
        for msg in messages:
            email_content = self.gmail_service.get_email_content(msg['id'])
            sender = email_content.get("from", "unknown")
            recipient = email_content.get("to", "unknown")
            subject = email_content.get("subject", "No subject")
            body = email_content.get("data", "")
            timestamp = email_content.get("timestamp", datetime.utcnow())

            # Store in DB
            self.db.save_email(msg['id'], sender, recipient, subject, timestamp, body)

            prompt = generate_reply_prompt(email_content['snippet'], body)

            if self.use_mock:
                reply = "🧪 This is a mock reply generated in test mode."
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                reply = response.choices[0].message.content.strip()

            print(f"Generated reply: {reply}")

            # Send reply if it's valid
            if recipient and sender and "@" in sender:
                self.gmail_service.send_email(sender, f"RE: {subject}", reply)
                self.slack_service.send_message('#general', f"📬 Replied to email from {sender}: {subject}")
            else:
                print(f"⚠️ Skipping send due to invalid 'To' field for email ID {msg['id']}")
