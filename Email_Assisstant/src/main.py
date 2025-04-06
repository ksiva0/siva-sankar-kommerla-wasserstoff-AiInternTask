# src/main.py

import os
import sys
import streamlit as st
import time
from streamlit_autorefresh import st_autorefresh

# Add the parent directory to sys.path to import services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.email_controller import EmailController

def main():
    st.set_page_config(page_title="Email Assistant", layout="centered")
    st.title("📧 Email Assistant")

    # Toggle for mock mode
    use_mock = st.sidebar.checkbox("🔧 Use Mock Mode", value=True)

    # Toggle for auto-run mode
    auto_mode = st.sidebar.checkbox("⏱️ Auto-reply every 60 seconds", value=False)

    # Load Slack token
    slack_token = os.environ.get("SLACK_BOT_TOKEN") or st.secrets["slack"]["SLACK_BOT_TOKEN"]
    if not slack_token:
        st.error("❌ Slack bot token is missing. Please set it in Streamlit secrets or as an environment variable.")
        return

    # Instantiate controller
    email_controller = EmailController(slack_token, use_mock=use_mock)

    # Auto-run background every 60 seconds
    if auto_mode:
        # This causes the app to rerun every 60 seconds
        st_autorefresh(interval=60000, limit=None, key="email_autorefresh")
        st.info("⏱️ Auto-run mode is ON. This page refreshes every 60 seconds to process emails.")
        email_controller.process_emails()
        st.success("✅ Auto-processed emails and replies sent!")

    # Manual trigger
    if st.button("📥 Process Emails Now"):
        email_controller.process_emails()
        st.success("✅ Emails processed and replies sent!")

if __name__ == "__main__":
    main()
