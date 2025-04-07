# email_assistant/src/controllers/email_controller.py

from services.gmail_service import fetch_emails
from services.slack_service import send_slack_message
from services.calendar_service import schedule_event
from services.web_search_service import perform_web_search
from utils.prompt_engineering import analyze_email
from utils.db import save_email, email_exists


def process_emails():
    emails = fetch_emails()
    for email in emails:
        if email_exists(email["id"]):
            continue

        save_email(email)
        analysis = analyze_email(email)

        if analysis["action"] == "reply":
            # send draft or send reply using gmail_service
            pass  # Placeholder
        elif analysis["action"] == "slack":
            send_slack_message(email)
        elif analysis["action"] == "schedule":
            schedule_event(analysis["event"])
        elif analysis["action"] == "search":
            results = perform_web_search(analysis["query"])
            # send results via reply or Slack
