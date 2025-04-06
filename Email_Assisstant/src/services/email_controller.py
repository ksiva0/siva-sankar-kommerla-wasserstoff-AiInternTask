# src/services/email_controller.py

from src.services.gmail_service import GmailService
from src.services.slack_service import SlackService
from src.services.calendar_service import CalendarService
from src.utils.prompt_engineering import generate_reply_prompt
import openai
import logging

class EmailController:
    def __init__(self, gmail_credentials, openai_api_key, slack_token):
        self.gmail_service = GmailService(gmail_credentials)
        openai.api_key = openai_api_key
        self.slack_service = SlackService(slack_token)
        self.calendar_service = CalendarService()
        self.logger = logging.getLogger(__name__)

    def fetch_emails(self):
        try:
            return self.gmail_service.get_emails()
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

    def send_to_slack(self, email, channel):
        try:
            message = f"New Email: Subject: {email['subject']}, From: {email['sender']}, Body: {email['body']}"
            self.slack_service.send_message(channel, message)
        except Exception as e:
            self.logger.error(f"Error sending to Slack: {e}")

    def schedule_meeting(self, email):
        # This is a placeholder. You'd integrate with the Calendar API here.
        print(f"Scheduling meeting based on email: {email['body']}")
        # Extract meeting details from the email using the LLM and then
        # use the Calendar API to create the event.
        # For example:
        # meeting_details = self._extract_meeting_details(email)
        # self.calendar_service.create_event(meeting_details)

    def _extract_meeting_details(self, email):
        prompt = f"Extract meeting details (date, time, title) from this email: {email['body']}. Return as a JSON object with keys 'date', 'time', and 'title'."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
