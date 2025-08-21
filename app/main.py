from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, credentials, email_accounts, credit_cards, devices

app = FastAPI(
    title="password_saver_api",
    description="API for managing passwords and credentials",
    version="1.0.0"
)

# ✅ Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],   # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers
)

# ✅ Include Routers
app.include_router(users.router)
app.include_router(credentials.router)
app.include_router(email_accounts.router)
app.include_router(credit_cards.router)
app.include_router(devices.router)