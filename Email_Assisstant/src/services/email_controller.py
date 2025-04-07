# src/services/email_controller.py

import logging
from services.gmail_service import GmailService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from utils.prompt_engineering import summarize_email_prompt, generate_reply_prompt, extract_meeting_prompt, call_llm

class EmailController:
    def __init__(self, credentials):
        self.logger = logging.getLogger(__name__)
        self.gmail_service = GmailService(credentials)
        self.slack_service = SlackService()
        self.calendar_service = CalendarService()

    def fetch_emails(self):
        emails = self.gmail_service.get_recent_emails()
        self.logger.info(f"Fetched {len(emails)} emails")
        return emails

    def draft_reply(self, email):
        prompt = generate_reply_prompt(email['body'], email['sender'])
        reply = call_llm(prompt)
        self.logger.info("Drafted reply using LLM")
        return reply

    def summarize_email(self, email):
        prompt = summarize_email_prompt(email['body'])
        summary = call_llm(prompt)
        self.logger.info("Generated summary using LLM")
        return summary

    def extract_meeting_details(self, email):
        prompt = extract_meeting_prompt(email['body'])
        meeting_data = call_llm(prompt, parse_json=True)
        event = self.calendar_service.create_event(meeting_data)
        self.logger.info("Scheduled event via CalendarService")
        return event

    def send_to_slack(self, email, channel):
        message = f"*New Email*\n*From:* {email['sender']}\n*Subject:* {email['subject']}\n\n{email['body']}"
        return self.slack_service.send_message(channel, message)

    def send_reply(self, email, reply_text):
        return self.gmail_service.send_email_reply(email, reply_text)
