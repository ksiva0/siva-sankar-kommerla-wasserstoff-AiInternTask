# Email_Assistant/src/main.py

from fastapi import FastAPI
from services.gmail_service import GmailService

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Email Assistant backend is running on Vercel"}
