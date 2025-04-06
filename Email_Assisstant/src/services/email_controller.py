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
        self.db = DatabaseService()

    def process_emails(self):
        messages = self.gmail_service.fetch_emails()
        for msg in messages:
            msg_id = msg['id']
            st.write("📩 Processing Message ID:", msg_id)

            if self.db.is_email_processed(msg_id):  # ⛔ Skip if already replied
                continue

            email_content = self.gmail_service.get_email_content(msg_id)
            sender = email_content.get("from", "unknown")
            recipient = email_content.get("to", "unknown")
            subject = email_content.get("subject", "No subject")
            body = email_content.get("data", "")
            snippet = email_content.get("snippet", "")
            timestamp = email_content.get("timestamp", datetime.utcnow())

            # Store in DB
            self.db.save_email(msg_id, sender, recipient, subject, timestamp, body)

            # Generate reply prompt
            prompt = generate_reply_prompt(snippet, body)

            if self.use_mock:
                reply = "🧪 This is a mock reply generated in test mode."
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                reply = response.choices[0].message.content.strip()

            print(f"🧠 Generated reply: {reply}")

            # Send reply if valid
            print(f"📧 Attempting to send email to: {sender}")
            print(f"From: {recipient}, Subject: {subject}, Generated Reply: {reply}")
            
            if recipient and sender and "@" in sender:
                try:
                    self.gmail_service.send_email(sender, f"RE: {subject}", reply)
                    print("✅ Email sent successfully.")
                except Exception as e:
                    print(f"❌ Failed to send email: {e}")
            else:
                print(f"⚠️ Skipping send due to invalid email fields. Sender: {sender}, Recipient: {recipient}")


            # Mark as processed
            self.db.mark_email_as_processed(msg_id)
