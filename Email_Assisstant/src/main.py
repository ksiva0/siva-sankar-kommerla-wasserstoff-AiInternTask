# src/main.py
import os
import sys
import streamlit as st

# Add the parent directory to sys.path to import services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.email_controller import EmailController

def main():
    st.set_page_config(page_title="Email Assistant", layout="centered")
    st.title("📧 Email Assistant")

    use_mock = st.sidebar.checkbox("🔧 Use Mock Mode", value=True)

    # Ask user to trigger email processing manually
    if st.button("📥 Process Emails Now"):
        try:
            slack_token = os.environ.get("SLACK_BOT_TOKEN") or st.secrets["slack"]["SLACK_BOT_TOKEN"]

            if not slack_token:
                st.error("Slack bot token is not set. Please set it in Streamlit secrets or as an environment variable.")
                return

            email_controller = EmailController(slack_token)
            email_controller.process_emails()

            st.success("✅ Emails processed and sent to Slack!")

        except Exception as e:
            st.error(f"🚨 Error: {e}")

if __name__ == "__main__":
    main()
