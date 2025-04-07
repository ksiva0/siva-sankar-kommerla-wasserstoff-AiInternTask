# src/services/slack_service.py

import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        slack_token = os.environ.get("SLACK_BOT_TOKEN")

        if not slack_token:
            raise EnvironmentError("SLACK_BOT_TOKEN must be set as an environment variable.")
        
        self.client = WebClient(token=slack_token)

    def send_message(self, channel, text):
        try:
            result = self.client.chat_postMessage(channel=channel, text=text)
            self.logger.info(f"✅ Slack message sent: {result['ts']}")
            return result
        except SlackApiError as e:
            self.logger.error(f"❌ Error sending Slack message: {e.response['error']}")
            return {"ok": False, "error": e.response['error']}
        except Exception as e:
            self.logger.error(f"Unexpected error sending Slack message: {e}")
            return {"ok": False, "error": str(e)}
