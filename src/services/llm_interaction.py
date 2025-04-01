import os
import openai  

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_email_context(email_body):  
    prompt = f"Analyze the following email content and provide a summary and actionable insights:\n\n{email_body}"  
    response = openai.ChatCompletion.create(  
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": prompt}]  
    )  
    return response.choices[0].message['content']
