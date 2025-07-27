from fastapi import APIRouter, HTTPException, status
from app.db import get_connection
from app.models.email_accounts import EmailAccountCreate, EmailAccountResponse, EmailAccountUpdate
from app.models.users import UserResponseModel

from datetime import datetime
from typing import List
import mysql.connector


router = APIRouter(prefix="/email_accounts", tags=["email_accounts"])

@router.get("/", response_model=List[EmailAccountResponse])
def get_email_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email_id, user_id, email_address, provider, recovery_email, two_factor_enabled, created_at FROM email_accounts")
        email_accounts = cursor.fetchall()
        return [
            EmailAccountResponse(
                email_id=ea[0],
                user_id=ea[1],
                email_address=ea[2],
                provider=ea[3],
                recovery_email=ea[4],
                two_factor_enabled=ea[5],
                created_at=ea[6]
            ) for ea in email_accounts
        ]
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()


@router.get("/{email_id}", response_model=EmailAccountResponse)
def get_email_account(email_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email_id, user_id, email_address, provider, recovery_email, two_factor_enabled, created_at FROM email_accounts WHERE email_id = %s", (email_id,))
        email_account = cursor.fetchone()
        if not email_account:
            raise HTTPException(status_code=404, detail="Email account not found")
        return EmailAccountResponse(
            email_id=email_account[0],
            user_id=email_account[1],
            email_address=email_account[2],
            provider=email_account[3],
            recovery_email=email_account[4],
            two_factor_enabled=email_account[5],
            created_at=email_account[6]
        )
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=EmailAccountResponse, status_code=status.HTTP_201_CREATED)
def create_email_account(email_account: EmailAccountCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO email_accounts (user_id, email_address, provider, recovery_email, two_factor_enabled, password_encrypted) VALUES (%s, %s, %s, %s, %s, %s)",
            (email_account.user_id, email_account.email_address, email_account.provider, email_account.recovery_email, email_account.two_factor_enabled, email_account.password_encrypted)
        )
        conn.commit()
        email_account_id = cursor.lastrowid
        return EmailAccountResponse(
            email_id=email_account_id,
            user_id=email_account.user_id,
            email_address=email_account.email_address,
            provider=email_account.provider,
            recovery_email=email_account.recovery_email,
            two_factor_enabled=email_account.two_factor_enabled,
            created_at=datetime.now()
        )
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()



@router.put("/{email_id}", response_model=EmailAccountResponse)
def update_email_account(email_id: int, email_account_update: EmailAccountUpdate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # First get the existing account to preserve unchanged fields
        cursor.execute("SELECT * FROM email_accounts WHERE email_id = %s", (email_id,))
        existing_account = cursor.fetchone()
        
        if not existing_account:
            raise HTTPException(status_code=404, detail="Email account not found")

        # Build the update query
        update_fields = []
        update_values = []
        
        fields_to_update = {
            "email_address": email_account_update.email_address,
            "provider": email_account_update.provider,
            "recovery_email": email_account_update.recovery_email,
            "two_factor_enabled": email_account_update.two_factor_enabled,
            "password_encrypted": email_account_update.password_encrypted
        }

        for field, value in fields_to_update.items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_query = f"UPDATE email_accounts SET {', '.join(update_fields)} WHERE email_id = %s"
        update_values.append(email_id)

        cursor.execute(update_query, tuple(update_values))
        conn.commit()

        # Get the updated record
        cursor.execute("SELECT * FROM email_accounts WHERE email_id = %s", (email_id,))
        updated_account = cursor.fetchone()

        return EmailAccountResponse(
            email_id=updated_account['email_id'],
            user_id=updated_account['user_id'],  # From database, not from update request
            email_address=updated_account['email_address'],
            provider=updated_account['provider'],
            recovery_email=updated_account['recovery_email'],
            two_factor_enabled=bool(updated_account['two_factor_enabled']),
            created_at=updated_account['created_at']  # From database
        )
        
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{email_id}", status_code=status.HTTP_200_OK)
def delete_email_account(email_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM email_accounts WHERE email_id = %s", (email_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Email account not found")
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()
    return {"detail": "Email account deleted successfully"}