import requests  

SLACK_BOT_TOKEN = 'YOUR_SLACK_BOT_TOKEN'  

def send_slack_message(channel, text):  
    headers = {  
        'Authorization': f'Bearer {SLACK_BOT_TOKEN}',  
        'Content-Type': 'application/json'  
    }  
    data = {  
        'channel': channel,  
        'text': text  
    }  
    response = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=data)  
    return response.json()
