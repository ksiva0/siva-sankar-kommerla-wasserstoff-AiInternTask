import os  
from slack_sdk import WebClient  

slack_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])  

async def notify_slack(message: str):  
    response = slack_client.chat_postMessage(channel='#general', text=message)  
    return response  
