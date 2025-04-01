from services.gmail_service import authenticate_gmail, fetch_emails
from services.llm_service import analyze_email_context  
from services.slack_service import send_slack_message  
from services.calendar_service import create_calendar_event  
from googleapiclient.discovery import build  
import datetime  

def main():  
    # Gmail Authentication  
    creds = authenticate_gmail()
    gmail_service = build('gmail', 'v1', credentials=creds)  
    
    # Email Fetching  
    emails = fetch_emails(gmail_service)  
    
    for email in emails:  
        insights = analyze_email_context(email['body'])  
        print(f"Insights for {email['subject']}:\n{insights}\n")  
        
        # Send Slack Notification  
        send_slack_message('#general', f"New email from {email['from']} with subject {email['subject']}")  
        
        # Example Calendar Event Creation (can be enhanced based on insights)  
        start_time = "2025-04-05T10:00:00-07:00"  
        end_time = "2025-04-05T11:00:00-07:00"  
        event_link = create_calendar_event(gmail_service, email['subject'], start_time, end_time)  
        print("Event created:", event_link)  

if __name__ == "__main__":  
    main()  
