# src/utils/prompt_engineering.py

def generate_reply_prompt(snippet, body):
    return f"""
You are an AI assistant. Here's the email snippet: "{snippet}"

Full email body:
\"\"\"
{body}
\"\"\"

Please:
1. Summarize the intent.
2. Draft a professional reply.
3. If the email asks to schedule a meeting, suggest a date/time.

Reply in plain text only.
"""
