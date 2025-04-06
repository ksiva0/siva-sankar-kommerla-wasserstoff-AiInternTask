# src/services/email_controller.py

import streamlit as st
from datetime import datetime
from openai import OpenAI

from services.gmail_service import GmailService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from services.database_service import DatabaseService
from utils.prompt_engineering import generate_reply_prompt


class EmailController:
    def __init__(self, slack_token: str, use_mock: bool = False):
        self.use_mock = use_mock
        self.gmail_service = GmailService(use_mock=use_mock)
        self.slack_service = SlackService(slack_token)
        self.calendar_service = CalendarService()
        self.db = DatabaseService()

        # Load OpenAI API Key from secrets
        self.openai_api_key = st.secrets["openai"]["OPENAI_API_KEY"]
        self.openai_client = OpenAI(api_key=self.openai_api_key)

    def process_emails(self):
        messages = self.gmail_service.fetch_emails()

        for msg in messages:
            msg_id = msg['id']
            st.write(f"📩 Processing Message ID: {msg_id}")

            # Skip if already processed
            if self.db.is_email_processed(msg_id):
                continue

            email_content = self.gmail_service.get_email_content(msg_id)
            sender = email_content.get("from", "unknown")
            recipient = email_content.get("to", "unknown")
            subject = email_content.get("subject", "No subject")
            body = email_content.get("data", "")
            snippet = email_content.get("snippet", "")
            timestamp = email_content.get("timestamp", datetime.utcnow())

            # Save to DB
            self.db.save_email(msg_id, sender, recipient, subject, timestamp, body)

            # Generate prompt and reply
            prompt = generate_reply_prompt(snippet, body)

            if self.use_mock:
                reply = "🧪 This is a mock reply generated in test mode."
            else:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=200,
                        temperature=0.7
                    )
                    reply = response.choices[0].message.content.strip()
                except Exception as e:
                    st.error(f"❌ Failed to generate reply using OpenAI: {e}")
                    continue

            st.write(f"🧠 Generated reply for `{subject}`:\n\n{reply}")

            # Attempt to send email
            if recipient and sender and "@" in sender:
                try:
                    self.gmail_service.send_email(
                        to=sender,
                        subject=f"RE: {subject}",
                        message_text=reply
                    )
                    st.success(f"✅ Reply sent to: {sender}")
                except Exception as e:
                    st.error(f"❌ Failed to send reply to {sender}: {e}")
            else:
                st.warning(f"⚠️ Skipped sending due to missing email info. From: {sender}, To: {recipient}")

            # Mark as processed
            self.db.mark_email_as_processed(msg_id)
