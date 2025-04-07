# src/main.py

import logging
import logging.config
from services.email_controller import EmailController
from google_auth_oauthlib.flow import Flow

# Load secrets manually from JSON or environment
import json
import os

with open("secrets.json") as f:
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

def main():
    print("### AI Email Assistant ###")

    logger.info(f"Redirect URI: {secrets['google_oauth']['redirect_uri']}")

    # --- OAuth Flow ---
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
        scopes=["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]
    )
    flow.redirect_uri = secrets["google_oauth"]["redirect_uri"]

    auth_url, _ = flow.authorization_url(prompt='consent')
    print(f"\n🔐 Please authorize the app by visiting this URL:\n{auth_url}")
    authorization_response = input("\nPaste the full redirect URL here after authorizing: ").strip()

    try:
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        print("✅ Authorization successful!")
        logger.info("Google OAuth authorization successful.")
    except Exception as e:
        print(f"❌ Failed to fetch token: {e}")
        logger.error(f"OAuth fetch_token error: {e}")
        return

    # --- Initialize email controller with credentials ---
    try:
        email_controller = EmailController(credentials=credentials)
    except Exception as e:
        print(f"❌ Error initializing services: {e}")
        logger.error(f"Error initializing services: {e}")
        return

    while True:
        print("\nSelect an action:")
        print("1. Read Emails")
        print("2. Draft Reply")
        print("3. Send to Slack")
        print("4. Summarize Email")
        print("5. Extract Meeting Details")
        print("6. Send Reply")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                emails = email_controller.fetch_emails()
                if emails:
                    for i, email in enumerate(emails):
                        print(f"\n--- Email {i+1} ---")
                        print(f"From: {email['sender']}")
                        print(f"Subject: {email['subject']}")
                        print(f"Date: {email['date']}")
                        print(f"Body:\n{email['body']}")
                else:
                    print("No emails found.")

            elif choice == "2":
                index = int(input("Enter email index to reply to: ")) - 1
                emails = email_controller.fetch_emails()
                if emails and 0 <= index < len(emails):
                    draft = email_controller.draft_reply(emails[index])
                    print("\nDraft Reply:")
                    print(draft)
                else:
                    print("Invalid index or no emails.")

            elif choice == "3":
                index = int(input("Enter email index to send to Slack: ")) - 1
                channel = input("Enter Slack channel (e.g., #general): ")
                emails = email_controller.fetch_emails()
                if emails and 0 <= index < len(emails):
                    result = email_controller.send_to_slack(emails[index], channel)
                    if result and result.get("ok"):
                        print("✅ Email sent to Slack.")
                    else:
                        print(f"❌ Failed to send email to Slack. Response: {result}")
                else:
                    print("Invalid index or no emails.")

            elif choice == "4":
                index = int(input("Enter email index to summarize: ")) - 1
                emails = email_controller.fetch_emails()
                if emails and 0 <= index < len(emails):
                    summary = email_controller.summarize_email(emails[index])
                    print("\nSummary:")
                    print(summary)
                else:
                    print("Invalid index or no emails.")

            elif choice == "5":
                index = int(input("Enter email index to extract meeting details from: ")) - 1
                emails = email_controller.fetch_emails()
                if emails and 0 <= index < len(emails):
                    meeting_details = email_controller.extract_meeting_details(emails[index])
                    print("\nMeeting Details:")
                    print(meeting_details)
                else:
                    print("Invalid index or no emails.")

            elif choice == "6":
                index = int(input("Enter email index to reply to: ")) - 1
                reply = input("Enter your reply: ")
                emails = email_controller.fetch_emails()
                if emails and 0 <= index < len(emails):
                    email_controller.send_reply(emails[index], reply)
                    print("✅ Reply sent.")
                else:
                    print("Invalid index or no emails.")

            elif choice == "0":
                print("👋 Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")

        except Exception as e:
            print(f"⚠️ Error: {e}")
            logger.error(f"Error during action: {e}")

if __name__ == "__main__":
    main()
