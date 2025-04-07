from fastapi import APIRouter, HTTPException  
from services.gmail_service import fetch_emails, reply_to_email  
from services.slack_service import notify_slack  

router = APIRouter()  

@router.get("/emails")  
async def get_emails():  
    try:  
        emails = await fetch_emails()  
        return emails  
    except Exception as e:  
        raise HTTPException(status_code=500, detail=str(e))  

@router.post("/reply")  
async def send_reply(email_id: str, reply_body: str):  
    try:  
        await reply_to_email(email_id, reply_body)  
        return {"message": "Reply sent!"}  
    except Exception as e:  
        raise HTTPException(status_code=400, detail=str(e))  

@router.post("/notify")  
async def notify_slack_message(message: str):  
    try:  
        await notify_slack(message)  
        return {"message": "Slack notification sent!"}  
    except Exception as e:  
        raise HTTPException(status_code=400, detail=str(e))  
