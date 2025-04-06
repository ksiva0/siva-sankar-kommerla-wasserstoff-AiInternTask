# src/utils/prompt_engineering.py

def generate_reply_prompt(email):
    return f"""
    You are an AI assistant helping to draft email replies.
    Here is the email:

    From: {email['sender']}
    Subject: {email['subject']}
    Body:
    {email['body']}

    Please draft a polite and concise reply.
    """

def generate_summary_prompt(email):
    return f"""
    You are an AI assistant helping to summarize emails.
    Here is the email:

    From: {email['sender']}
    Subject: {email['subject']}
    Body:
    {email['body']}

    Please provide a concise summary of the email's main points.
    """

def generate_meeting_details_prompt(email):
    return f"""
    You are an AI assistant helping to extract meeting details from emails.
    Here is the email:

    From: {email['sender']}
    Subject: {email['subject']}
    Body:
    {email['body']}

    Please extract any meeting details, including date, time, and topic.
    If there are no meeting details, say "No meeting details found".
    """
