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
    st.title("📧 AI Email Assistant")

    # Sidebar options
    st.sidebar.header("Settings")
    use_mock = st.sidebar.checkbox("🔧 Use Mock Mode", value=False)
    auto_mode = st.sidebar.checkbox("⏱️ Auto-reply every 60 seconds", value=False)

    # Load Slack token
    slack_token = st.secrets.get("slack", {}).get("SLACK_BOT_TOKEN")
    if not slack_token:
        st.error("❌ Slack bot token is missing. Please add it to your Streamlit secrets.")
        return

    # Initialize the email controller
    try:
        email_controller = EmailController(slack_token, use_mock=use_mock)
    except Exception as e:
        st.error(f"❌ Failed to initialize Email Controller: {e}")
        return

    # Auto mode: refresh every 60 seconds
    if auto_mode:
        st_autorefresh(interval=60000, limit=None, key="email_autorefresh")
        st.info("⏱️ Auto-run is enabled. This page refreshes every 60 seconds.")
        try:
            email_controller.process_emails()
            st.success("✅ Emails auto-processed and replies sent!")
        except Exception as e:
            st.error(f"❌ Auto-processing failed: {e}")

    # Manual trigger
    if st.button("📥 Process Emails Now"):
        try:
            email_controller.process_emails()
            st.success("✅ Emails processed and replies sent!")
        except Exception as e:
            st.error(f"❌ Manual processing failed: {e}")

if __name__ == "__main__":
    main()
