from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum

class DeviceType(str, Enum):
    LAPTOP = 'Laptop'
    DESKTOP = 'Desktop'
    TABLET = 'Tablet'
    OTHER = 'Other'

class DeviceBase(BaseModel):
    """Shared fields for all device models"""
    device_type: DeviceType = Field('Laptop', description="Type of device")
    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    operating_system: Optional[str] = Field(None, max_length=50)
    purchase_date: Optional[date] = None
    notes: Optional[str] = None

class DeviceCreate(DeviceBase):
    """Model for creating new devices (includes required fields)"""
    user_id: int
    admin_password_encrypted: str = Field(..., description="Encrypted admin password")

class DeviceResponse(DeviceBase):
    """Model for API responses (excludes sensitive data)"""
    device_id: int
    user_id: int
    created_at: datetime

class DeviceUpdate(BaseModel):
    """Model for updating devices (all fields optional)"""
    device_type: Optional[DeviceType] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    operating_system: Optional[str] = None
    admin_password_encrypted: Optional[str] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = None