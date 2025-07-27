from fastapi import APIRouter, HTTPException, status
from app.db import get_connection
from app.models.credentials import CredentialCreate,CredentialResponse, CredentialUpdate
from app.models.users import UserResponseModel

from datetime import datetime
from typing import List
import mysql.connector


router = APIRouter(prefix="/credentials", tags=["credentials"])

@router.get("/", response_model=List[CredentialResponse])
def get_credentials():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT credential_id, user_id, title, username, url, notes, password_encrypted, created_at FROM credentials")
        credentials = cursor.fetchall()
        return [
            CredentialResponse(
                credential_id=cred[0],
                user_id=cred[1],
                title=cred[2],
                username=cred[3],
                url=cred[4],
                notes=cred[5],
                password_encrypted=cred[6],
                created_at=cred[7]
            ) for cred in credentials
        ]
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.get("/{credential_id}", response_model=CredentialResponse)
def get_credential(credential_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT credential_id, user_id, title, username, url, notes, password_encrypted, created_at FROM credentials WHERE credential_id = %s", (credential_id,))
        cred = cursor.fetchone()
        if not cred:
            raise HTTPException(status_code=404, detail="Credential not found")
        return CredentialResponse(
            credential_id=cred[0],
            user_id=cred[1],
            title=cred[2],
            username=cred[3],
            url=cred[4],
            notes=cred[5],
            password_encrypted=cred[6],
            created_at=cred[7]
        )
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=CredentialResponse, status_code=status.HTTP_201_CREATED)
def create_credential(credential: CredentialCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # First verify the user exists
        cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (credential.user_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Insert the credential
        cursor.execute(
            """INSERT INTO credentials 
            (user_id, title, username, url, notes, password_encrypted) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (credential.user_id, credential.title, credential.username, 
             credential.url, credential.notes, credential.password_encrypted)
        )
        conn.commit()
        credential_id = cursor.lastrowid

        # Get the created_at timestamp from database
        cursor.execute(
            "SELECT created_at FROM credentials WHERE credential_id = %s",
            (credential_id,)
        )
        created_at = cursor.fetchone()[0]

        return CredentialResponse(
            credential_id=credential_id,
            user_id=credential.user_id,
            title=credential.title,
            username=credential.username,
            url=credential.url,
            notes=credential.notes,
            created_at=created_at  # Use the actual DB timestamp
        )

    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}"
        )
    finally:
        cursor.close()
        conn.close()


@router.put("/{credential_id}", response_model=CredentialResponse)
def update_credential(credential_id: int, credential: CredentialUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check if the credential exists
        cursor.execute("SELECT 1 FROM credentials WHERE credential_id = %s", (credential_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Credential not found")

        # Update the credential
        cursor.execute(
            """UPDATE credentials 
            SET title = %s, username = %s, url = %s, notes = %s, password_encrypted = %s 
            WHERE credential_id = %s""",
            (credential.title, credential.username, credential.url, 
             credential.notes, credential.password_encrypted, credential_id)
        )
        conn.commit()

        # Get the updated credential data
        cursor.execute(
            "SELECT user_id, title, username, url, notes, password_encrypted, created_at FROM credentials WHERE credential_id = %s",
            (credential_id,)
        )
        cred_data = cursor.fetchone()

        return CredentialResponse(
            credential_id=credential_id,
            user_id=cred_data[0],
            title=cred_data[1],
            username=cred_data[2],
            url=cred_data[3],
            notes=cred_data[4],
            password_encrypted=cred_data[5],
            created_at=cred_data[6]  # Use the actual DB timestamp
        )

    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{credential_id}", status_code=status.HTTP_200_OK)
def delete_credential(credential_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM credentials WHERE credential_id = %s", (credential_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Credential not found")
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()
    return {"detail": "Credential deleted successfully"}