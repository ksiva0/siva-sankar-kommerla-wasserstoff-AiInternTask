# src/services/email_controller.py

from services.gmail_service import GmailService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from utils.prompt_engineering import generate_reply_prompt, generate_summary_prompt, generate_meeting_details_prompt
import openai
import logging
import streamlit as st

class EmailController:
    def __init__(self):
        self.gmail_service = GmailService()
        openai.api_key = st.secrets["openai"]["OPENAI_API_KEY"]
        self.slack_service = SlackService()
        self.calendar_service = CalendarService()
        self.logger = logging.getLogger(__name__)

    def fetch_emails(self):
        try:
            messages = self.gmail_service.list_messages()
            if messages:
                emails = []
                for message in messages:
                    full_message = self.gmail_service.get_message(message['id'])
                    if full_message:
                        email_data = self.gmail_service.get_email_data(full_message)
                        emails.append(email_data)
                return emails
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return None

    def draft_reply(self, email):
        try:
            prompt = generate_reply_prompt(email)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Or "gpt-4"
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error generating reply: {e}")
            return "Error drafting reply."

    def summarize_email(self, email):
        try:
            prompt = generate_summary_prompt(email)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error summarizing email: {e}")
            return "Error summarizing email."

    def extract_meeting_details(self, email):
        try:
            prompt = generate_meeting_details_prompt(email)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error extracting meeting details: {e}")
            return "Error extracting meeting details."

    def send_to_slack(self, email, channel):
        try:
            message = f"New Email:\nSubject: {email['subject']}\nFrom: {email['sender']}\nBody:\n{email['body']}"
            self.slack_service.send_message(channel, message)
        except Exception as e:
            self.logger.error(f"Error sending to Slack: {e}")

    def send_reply(self, email, reply_text):
        try:
            self.gmail_service.send_message(
                to=email['sender'],
                subject=f"Re: {email['subject']}",
                message_body=reply_text
            )
        except Exception as e:
            self.logger.error(f"Error sending reply: {e}")
