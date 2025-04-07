# Email_Assistant/src/main.py

from fastapi import FastAPI
from controllers.email_controller import router as email_router

app = FastAPI()

app.include_router(email_router)

@app.get("/")
def root():
    return {"message": "Email Assistant backend is running on Vercel"}
