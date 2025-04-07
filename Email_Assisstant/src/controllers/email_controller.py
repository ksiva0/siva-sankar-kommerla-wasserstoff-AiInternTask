# Email_Assistant/src/controllers/email_controller.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/emails")
def read_emails():
    return {"message": "Emails would be fetched here"}
