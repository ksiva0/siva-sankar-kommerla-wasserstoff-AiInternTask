# src/services/slack_service.py

import requests
import streamlit as st

class SlackService:
    def __init__(self, token=None):
        # Token can be passed or fetched from Streamlit secrets
        self.token = token or st.secrets["slack"]["SLACK_BOT_TOKEN"]

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

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()

            if not response_data.get("ok"):
                st.error(f"Slack API Error: {response_data.get('error')}")
            return response_data

        except requests.RequestException as e:
            st.error(f"⚠️ Failed to send message to Slack: {e}")
            return {"ok": False, "error": str(e)}
