from fastapi import FastAPI
from app.routers import users, credentials,email_accounts,credit_cards,devices


app = FastAPI(
    title="password_saver_api",
    description="API for managing passwords and credentials",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(credentials.router)
app.include_router(email_accounts.router)
app.include_router(credit_cards.router)
app.include_router(devices.router)
