from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EmailAccountBase(BaseModel):
    """Base model with common fields"""
    email_address: str
    provider: Optional[str] = None
    recovery_email: Optional[str] = None
    two_factor_enabled: bool = False

class EmailAccountCreate(EmailAccountBase):
    """Model for creating email accounts (includes required fields)"""
    user_id: int
    password_encrypted: str

class EmailAccountResponse(EmailAccountBase):
    """Model for API responses (excludes sensitive data)"""
    email_id: int
    user_id: int
    created_at: datetime

class EmailAccountUpdate(BaseModel):
    """Model for updating email accounts (all fields optional)"""
    email_address: Optional[str] = None
    provider: Optional[str] = None
    password_encrypted: Optional[str] = None
    recovery_email: Optional[str] = None
    two_factor_enabled: Optional[bool] = None
    # Note: user_id is intentionally excluded from updates