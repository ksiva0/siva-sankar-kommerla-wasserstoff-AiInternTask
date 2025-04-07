from fastapi import FastAPI  
from controllers.email_controller import router as email_router  

app = FastAPI()  

# Register the email router  
app.include_router(email_router)  
