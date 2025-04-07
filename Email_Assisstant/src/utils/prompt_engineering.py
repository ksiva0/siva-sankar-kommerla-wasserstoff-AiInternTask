# email_assistant/src/utils/prompt_engineering.py

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


def analyze_email(email):
    prompt = f"""
You are an email assistant. Analyze the following email and decide:
- Is it asking for info (search)?
- Should we reply?
- Is it requesting a meeting (schedule)?
- Should we forward it to Slack?

Email:
From: {email['sender']}
Subject: {email['subject']}
Snippet: {email['snippet']}

Respond with a JSON like: {{"action": "reply|slack|schedule|search", "query/event": "..."}}
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return eval(response["choices"][0]["message"]["content"])
    except:
        return {"action": "slack"}
