from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CredentialBase(BaseModel):
    """Base model with common fields"""
    title: Optional[str] = None
    username: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None

class CredentialCreate(CredentialBase):
    """Model for creating credentials (includes required fields)"""
    user_id: int
    password_encrypted: str

class CredentialResponse(CredentialBase):
    """Model for returning credential data (includes read-only fields)"""
    credential_id: int
    user_id: int
    created_at: datetime

class CredentialUpdate(CredentialBase):
    """Model for updating credentials (all fields optional)"""
    password_encrypted: Optional[str] = None