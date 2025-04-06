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
