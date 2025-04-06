# src/main.py

import os
import sys
import streamlit as st
import time

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

    # Manual trigger
    if st.button("📥 Process Emails Now"):
        email_controller.process_emails()
        st.success("✅ Emails processed and replies sent!")

    # Auto-run background every 60 seconds
    if auto_mode:
        st.info("⏱️ Auto-reply mode is ON. This page checks for emails every 60 seconds.")

        # Track last run time to avoid constant reruns
        if 'last_run' not in st.session_state:
            st.session_state['last_run'] = 0

        # Check if 60 seconds have passed since last run
        if time.time() - st.session_state['last_run'] > 60:
            email_controller.process_emails()
            st.session_state['last_run'] = time.time()
            st.experimental_rerun()  # reruns the script to check again

if __name__ == "__main__":
    main()
