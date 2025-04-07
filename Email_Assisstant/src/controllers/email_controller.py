# Email_Assistant/src/controllers/email_controller.py

from fastapi import APIRouter
from services.gmail_service import GmailService
from utils.prompt_engineering import generate_prompt

router = APIRouter()

@router.get("/emails")
def read_emails():
    return {"message": "Emails would be fetched here"}
