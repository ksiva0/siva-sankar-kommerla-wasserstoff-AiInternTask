# src/services/email_controller.py

import os
from openai import OpenAI
import streamlit as st
from services.gmail_service import GmailService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from utils.prompt_engineering import generate_reply_prompt

class EmailController:
    def __init__(self, slack_token):
        self.gmail_service = GmailService()
        self.slack_service = SlackService(slack_token)
        self.calendar_service = CalendarService()

        # Use OpenAI API key from Streamlit secrets
        self.openai_api_key = st.secrets["openai"]["OPENAI_API_KEY"]
        self.client = OpenAI(OPENAI_API_KEY=self.openai_api_key)

    def process_emails(self):
        messages = self.gmail_service.fetch_emails()
        for msg in messages:
            email_content = self.gmail_service.get_email_content(msg['id'])
            print(f"📩 Processing email ID: {msg['id']}")

            prompt = generate_reply_prompt(email_content['snippet'], email_content['data'])

            # Use the updated OpenAI SDK client call
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )

            reply = response.choices[0].message.content
            print(f"✅ Generated reply: {reply}")

            self.gmail_service.send_email(
                to=email_content['data'].split()[0],
                subject="RE: " + email_content['snippet'],
                body=reply
            )
            self.slack_service.send_message(
                channel='#general',
                message=f"Replied to email ID: {msg['id']}"
            )
