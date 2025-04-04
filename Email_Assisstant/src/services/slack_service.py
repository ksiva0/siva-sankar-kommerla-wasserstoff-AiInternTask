# src/services/slack_service.py
import requests

class SlackService:
    def __init__(self, token):
        self.token = token

    def send_message(self, channel, text):
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": channel,
            "text": text
        }
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        if not response_data.get("ok"):
            print(f"Slack API Error: {response_data.get('error')}")
        return response_data