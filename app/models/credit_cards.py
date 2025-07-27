from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum

class CardType(str, Enum):
    CREDIT = 'Credit'
    DEBIT = 'Debit'
    PREPAID = 'Prepaid'

class CreditCardBase(BaseModel):
    card_holder_name: Optional[str] = Field(None, max_length=100)
    expiration_date: Optional[date] = None
    billing_address: Optional[str] = None
    card_type: Optional[CardType] = Field('Credit')

class CreditCardCreateRequest(BaseModel):
    """Request model that accepts frontend field names"""
    user_id: int
    card_number: str = Field(..., description="Card number (will be encrypted)")
    cvv: str = Field(..., description="CVV (will be encrypted)")
    card_holder_name: Optional[str] = Field(None, max_length=100)
    expiration_date: Optional[date] = None
    billing_address: Optional[str] = None
    card_type: Optional[CardType] = Field('Credit')

class CreditCardCreateDB(CreditCardBase):
    """Model for database insertion with encrypted field names"""
    user_id: int
    card_number_encrypted: str
    cvv_encrypted: str

class CreditCardResponse(CreditCardBase):
    card_id: int
    user_id: int
    created_at: datetime