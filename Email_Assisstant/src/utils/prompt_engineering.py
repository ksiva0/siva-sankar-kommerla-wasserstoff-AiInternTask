# src/utils/prompt_engineering.py
def generate_reply_prompt(subject, body):
    return f"""
    Hello.

    Subject: {subject}
    Body: {body}

    Reply:
    """
