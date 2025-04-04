# src/services/email_controller.py
import openai
import os
from services.gmail_service import GmailService
from services.slack_service import SlackService
from services.calendar_service import CalendarService
from utils.prompt_engineering import generate_reply_prompt

class EmailController:
    def __init__(self, slack_token):
        self.gmail_service = GmailService()
        self.slack_service = SlackService(slack_token)
        self.calendar_service = CalendarService()

        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is missing. Set OPENAI_API_KEY in environment variables.")

        openai.api_key = self.openai_api_key

    def process_emails(self):
        messages = self.gmail_service.fetch_emails()
        for msg in messages:
            email_content = self.gmail_service.get_email_content(msg['id'])
            print(f"Processing email ID: {msg['id']}")

            prompt = generate_reply_prompt(email_content['snippet'], email_content['data'])
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            reply = response['choices'][0]['message']['content']
            print(f"Generated reply: {reply}")

            self.gmail_service.send_email(email_content['data'].split()[0], "RE: " + email_content['snippet'], reply)
            self.slack_service.send_message('#general', f"Replied to email ID: {msg['id']}")