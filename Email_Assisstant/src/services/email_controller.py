from openai import OpenAI
import streamlit as st

class EmailController:
    def __init__(self, slack_token):
        self.gmail_service = GmailService()
        self.slack_service = SlackService(slack_token)
        self.calendar_service = CalendarService()

        self.client = OpenAI(api_key=st.secrets["openai"]["OPENAI_API_KEY"])

    def process_emails(self):
        messages = self.gmail_service.fetch_emails()
        for msg in messages:
            email_content = self.gmail_service.get_email_content(msg['id'])
            print(f"Processing email ID: {msg['id']}")

            prompt = generate_reply_prompt(email_content['snippet'], email_content['data'])
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            reply = response.choices[0].message.content
            print(f"Generated reply: {reply}")

            self.gmail_service.send_email(email_content['data'].split()[0], "RE: " + email_content['snippet'], reply)
            self.slack_service.send_message('#general', f"Replied to email ID: {msg['id']}")
