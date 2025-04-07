# src/main.py

import logging
import logging.config
from services.email_controller import EmailController
from google_auth_oauthlib.flow import Flow
import json
import os

# Load credentials from a config file (instead of Streamlit secrets)
with open("config/credentials.json") as f:
    secrets = json.load(f)

# Configure logging
logging_config = {
    'version': 1,
    'formatters': {
        'standard': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
            'filename': 'app.log',
            'mode': 'w'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO'
    }
}
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

def authenticate():
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": secrets["google_oauth"]["client_id"],
                "client_secret": secrets["google_oauth"]["client_secret"],
                "redirect_uris": [secrets["google_oauth"]["redirect_uri"]],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.modify"]
    )
    flow.redirect_uri = secrets["google_oauth"]["redirect_uri"]

    auth_url, _ = flow.authorization_url(prompt='consent')
    print(f"Please go to this URL and authorize access:\n{auth_url}")

    authorization_response = input("Paste the full redirect URL here: ")
    flow.fetch_token(authorization_response=authorization_response)
    logger.info("Google OAuth authorization successful.")
    return flow.credentials

def main():
    print("Initializing AI Email Assistant...")
    try:
        credentials = authenticate()
    except Exception as e:
        logger.error(f"OAuth fetch_token error: {e}")
        return

    try:
        email_controller = EmailController(credentials=credentials)
    except Exception as e:
        logger.error(f"Error initializing email controller: {e}")
        return

    print("Choose an action:")
    actions = [
        "Read Emails", "Draft Reply", "Send to Slack",
        "Summarize Email", "Extract Meeting Details", "Send Reply"
    ]
    for i, act in enumerate(actions):
        print(f"{i+1}. {act}")
    choice = int(input("Enter the action number: "))

    try:
        emails = email_controller.fetch_emails()
        if not emails:
            print("No emails found.")
            return
        email_index = int(input(f"Choose email index (1 to {len(emails)}): ")) - 1
        if email_index < 0 or email_index >= len(emails):
            print("Invalid email index.")
            return
        selected_email = emails[email_index]
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        return

    try:
        if choice == 1:
            print(selected_email)
        elif choice == 2:
            reply = email_controller.draft_reply(selected_email)
            print("Drafted Reply:\n", reply)
        elif choice == 3:
            channel = input("Enter Slack channel: ")
            result = email_controller.send_to_slack(selected_email, channel)
            print("Slack Result:", result)
        elif choice == 4:
            summary = email_controller.summarize_email(selected_email)
            print("Summary:\n", summary)
        elif choice == 5:
            meeting = email_controller.extract_meeting_details(selected_email)
            print("Meeting Details:\n", meeting)
        elif choice == 6:
            reply_text = input("Enter your reply: ")
            email_controller.send_reply(selected_email, reply_text)
            print("Reply sent.")
        else:
            print("Invalid choice.")
    except Exception as e:
        logger.error(f"Error performing action: {e}")

if __name__ == "__main__":
    main()
