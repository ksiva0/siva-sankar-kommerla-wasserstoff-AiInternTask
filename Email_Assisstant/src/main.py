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

    # Add Mock Mode toggle
    use_mock = st.sidebar.checkbox("🔧 Use Mock Mode", value=True)

    # Add Auto-run toggle
    auto_mode = st.sidebar.checkbox("⏱️ Auto-run Every 60 Seconds", value=False)

    # Slack token setup
    slack_token = os.environ.get("SLACK_BOT_TOKEN") or st.secrets["slack"]["SLACK_BOT_TOKEN"]
    if not slack_token:
        st.error("Slack bot token is not set. Please set it in Streamlit secrets or as an environment variable.")
        return

    email_controller = EmailController(slack_token, use_mock=use_mock)

    # Manual button
    if st.button("📥 Process Emails Now"):
        email_controller.process_emails()
        st.success("✅ Emails processed manually!")

    if auto_mode:
        st.info("⏱️ Auto-run mode is ON. This page will refresh every 60 seconds to process emails.")
        
        if 'last_run' not in st.session_state:
            st.session_state['last_run'] = time.time()
    
        # Run only if 60 seconds have passed
        if time.time() - st.session_state['last_run'] > 60:
            email_controller.process_emails()
            st.session_state['last_run'] = time.time()
            st.experimental_rerun()

if __name__ == "__main__":
    main()
