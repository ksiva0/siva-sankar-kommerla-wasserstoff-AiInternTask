# src/services/slack_service.py

from slack_sdk import WebClient
import logging
import requests
import streamlit as st

class SlackService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = WebClient(token=st.secrets["slack"]["SLACK_BOT_TOKEN"])

    def send_message(self, channel, text):
        try:
            result = self.client.chat_postMessage(channel=channel, text=text)
            self.logger.info(f"Slack message sent: {result['ts']}")
            return result
        except Exception as e:
            self.logger.error(f"Error sending Slack message: {e}")
            st.error(f"⚠️ Failed to send message to Slack: {e}")
            return {"ok": False, "error": str(e)}
