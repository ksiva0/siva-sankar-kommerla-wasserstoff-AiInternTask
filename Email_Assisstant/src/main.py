# src/main.py

import streamlit as st
from services.email_controller import EmailController
from google_auth_oauthlib.flow import Flow
import logging
import logging.config

# Configure logging
logging_config = {
    'version': 1,
    'formatters': {
        'standard': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
            'filename': 'app.log',
            'mode': 'w'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO'
    }
}
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

def main():
    st.title("AI Email Assistant")

    logger.info(f"Redirect URI from secrets: {st.secrets['google_oauth']['redirect_uri']}")

    # --- OAuth Flow ---
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=["https://www.googleapis.com/auth/gmail.readonly"]
    )
    flow.redirect_uri = st.secrets["google_oauth"]["redirect_uri"]

    auth_url, _ = flow.authorization_url(prompt='consent')
    st.markdown(f"[Click here to authorize Gmail access]({auth_url})")

    authorization_response = st.text_input("Paste the full redirect URL here after authorizing:")

    if authorization_response:
        try:
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            st.success("✅ Authorization successful!")
            logger.info("Google OAuth authorization successful.")
        except Exception as e:
            st.error(f"❌ Failed to fetch token: {e}")
            logger.error(f"OAuth fetch_token error: {e}")
            return
    else:
        st.warning("👆 Please authorize Gmail and paste the full redirect URL to proceed.")
        return

    # --- Initialize email controller with credentials ---
    try:
        email_controller = EmailController(credentials=credentials)
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        logger.error(f"Error initializing services: {e}")
        return

    action = st.selectbox("Choose an action:", [
        "Read Emails", "Draft Reply", "Send to Slack", 
        "Summarize Email", "Extract Meeting Details", "Send Reply"
    ])

    if action == "Read Emails":
        if st.button("Fetch and Display Emails"):
            try:
                emails = email_controller.fetch_emails()
                if emails:
                    for i, email in enumerate(emails):
                        st.subheader(f"Email {i+1}")
                        st.write(f"From: {email['sender']}")
                        st.write(f"Subject: {email['subject']}")
                        st.write(f"Date: {email['date']}")
                        with st.expander("Body"):
                            st.write(email['body'])
                        st.write("---")
                else:
                    st.info("No emails found.")
            except Exception as e:
                st.error(f"Error fetching emails: {e}")
                logger.error(f"Error fetching emails: {e}")

    elif action == "Draft Reply":
        email_index = st.number_input("Enter the email index to reply to:", min_value=1, value=1, step=1) - 1
        if st.button("Draft Reply"):
            try:
                emails = email_controller.fetch_emails()
                if emails and 0 <= email_index < len(emails):
                    draft_reply = email_controller.draft_reply(emails[email_index])
                    st.subheader("Draft Reply:")
                    st.write(draft_reply)
                else:
                    st.info("No emails to reply to or invalid email index.")
            except Exception as e:
                st.error(f"Error drafting reply: {e}")
                logger.error(f"Error drafting reply: {e}")

    elif action == "Send to Slack":
        email_index = st.number_input("Enter the email index to send to Slack:", min_value=1, value=1, step=1) - 1
        slack_channel = st.text_input("Enter the Slack channel to send to:")
        if st.button("Send to Slack"):
            try:
                emails = email_controller.fetch_emails()
                if emails and 0 <= email_index < len(emails):
                    result = email_controller.send_to_slack(emails[email_index], slack_channel)
                    if result and result.get("ok"):
                        st.success("Email sent to Slack!")
                    else:
                        st.error(f"Failed to send email to slack. Result: {result}")
                else:
                    st.info("No emails to send to Slack or invalid email index.")
            except Exception as e:
                st.error(f"Error sending to Slack: {e}")
                logger.error(f"Error sending to Slack: {e}")

    elif action == "Summarize Email":
        email_index = st.number_input("Enter the email index to summarize:", min_value=1, value=1, step=1) - 1
        if st.button("Summarize Email"):
            try:
                emails = email_controller.fetch_emails()
                if emails and 0 <= email_index < len(emails):
                    summary = email_controller.summarize_email(emails[email_index])
                    st.subheader("Email Summary:")
                    st.write(summary)
                else:
                    st.info("No emails to summarize or invalid email index.")
            except Exception as e:
                st.error(f"Error summarizing email: {e}")
                logger.error(f"Error summarizing email: {e}")

    elif action == "Extract Meeting Details":
        email_index = st.number_input("Enter the email index to extract meeting details from:", min_value=1, value=1, step=1) - 1
        if st.button("Extract Meeting Details"):
            try:
                emails = email_controller.fetch_emails()
                if emails and 0 <= email_index < len(emails):
                    meeting_details = email_controller.extract_meeting_details(emails[email_index])
                    st.subheader("Meeting Details:")
                    st.write(meeting_details)
                else:
                    st.info("No emails or invalid email index.")
            except Exception as e:
                st.error(f"Error extracting meeting details: {e}")
                logger.error(f"Error extracting meeting details: {e}")

    elif action == "Send Reply":
        email_index = st.number_input("Enter the email index to reply to:", min_value=1, value=1, step=1) - 1
        reply_text = st.text_area("Enter your reply:")
        if st.button("Send Reply"):
            try:
                emails = email_controller.fetch_emails()
                if emails and 0 <= email_index < len(emails):
                    email_controller.send_reply(emails[email_index], reply_text)
                    st.success("Reply sent!")
                else:
                    st.info("No emails or invalid email index.")
            except Exception as e:
                st.error(f"Error sending reply: {e}")
                logger.error(f"Error sending reply: {e}")

if __name__ == "__main__":
    main()
