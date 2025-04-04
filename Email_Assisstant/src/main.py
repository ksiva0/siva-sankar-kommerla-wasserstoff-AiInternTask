# src/main.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.email_controller import EmailController

if __name__ == "__main__":
    try:
        slack_token = os.environ.get("SLACK_BOT_TOKEN")
        if not slack_token:
            raise ValueError("Slack bot token is not set. Please set the SLACK_BOT_TOKEN environment variable.")

        email_controller = EmailController(slack_token)
        email_controller.process_emails()
    except Exception as e:
        print(f"An error occurred: {e}")