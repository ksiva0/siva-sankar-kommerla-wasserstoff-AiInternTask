# Email_Assistant/src/services/slack_service.py

import os
import requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")


def send_slack_message(email):
    message = f"New Email from {email['sender']}\nSubject: {email['subject']}\nSnippet: {email['snippet']}"
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    data = {"channel": SLACK_CHANNEL, "text": message}
    requests.post(url, headers=headers, data=data)
