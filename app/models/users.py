from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreateModel(BaseModel):
    """Model for user creation input"""
    username: str
    master_password_hash: str
    email: Optional[str] = None

class UserResponseModel(BaseModel):
    """Model for API responses (excludes sensitive data)"""
    user_id: int
    username: str
    email: Optional[str] = None
    created_at: datetime