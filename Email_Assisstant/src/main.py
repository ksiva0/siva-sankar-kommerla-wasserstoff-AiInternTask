# src/main.py

import streamlit as st
from services.email_controller import EmailController
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

def main():
    st.title("AI Email Assistant")

    # Initialize services (replace with your actual credentials)
    try:
        email_controller = EmailController(
            gmail_credentials=None,  # Replace with your Gmail credentials logic
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            slack_token=os.getenv("SLACK_BOT_TOKEN")
        )
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return

    # User input for actions
    action = st.selectbox("Choose an action:", ["Read Emails", "Draft Reply", "Send to Slack"])

    if action == "Read Emails":
        if st.button("Fetch and Display Emails"):
            try:
                emails = email_controller.fetch_emails()
                if emails:
                    for email in emails:
                        st.subheader(f"Subject: {email['subject']}")
                        st.write(f"From: {email['sender']}")
                        st.write(email['body'])
                        st.write("---")
                else:
                    st.info("No emails found.")
            except Exception as e:
                st.error(f"Error fetching emails: {e}")

    elif action == "Draft Reply":
        email_index = st.number_input("Enter the email index to reply to:", min_value=0, value=0)
        if st.button("Draft Reply"):
            try:
                emails = email_controller.fetch_emails()
                if emails:
                    draft_reply = email_controller.draft_reply(emails[email_index])
                    st.subheader("Draft Reply:")
                    st.write(draft_reply)
                else:
                    st.info("No emails to reply to.")
            except Exception as e:
                st.error(f"Error drafting reply: {e}")

    elif action == "Send to Slack":
        email_index = st.number_input("Enter the email index to send to Slack:", min_value=0, value=0)
        slack_channel = st.text_input("Enter the Slack channel to send to:")
        if st.button("Send to Slack"):
            try:
                emails = email_controller.fetch_emails()
                if emails:
                    email_controller.send_to_slack(emails[email_index], slack_channel)
                    st.success("Email sent to Slack!")
                else:
                    st.info("No emails to send to Slack.")
            except Exception as e:
                st.error(f"Error sending to Slack: {e}")

if __name__ == "__main__":
    main()
