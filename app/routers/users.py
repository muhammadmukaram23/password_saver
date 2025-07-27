from fastapi import APIRouter, HTTPException, status
from app.db import get_connection
from app.models.users import  UserCreateModel, UserResponseModel
from datetime import datetime
from typing import List
import mysql.connector


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponseModel])
def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, username, email, created_at FROM users")
        users = cursor.fetchall()
        return [
            UserResponseModel(
                user_id=user[0],
                username=user[1],
                email=user[2],
                created_at=user[3]
            ) for user in users
        ]
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.get("/{user_id}", response_model=UserResponseModel)
def get_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, username, email, created_at FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponseModel(
            user_id=user[0],
            username=user[1],
            email=user[2],
            created_at=user[3]
        )
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreateModel):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, master_password_hash, email) VALUES (%s, %s, %s)",
            (user.username, user.master_password_hash, user.email)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        # Fetch the created user to get the actual created_at timestamp
        cursor.execute("SELECT username, email, created_at FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        return UserResponseModel(
            user_id=user_id,
            username=user_data[0],
            email=user_data[1],
            created_at=user_data[2]  # Use the actual DB timestamp
        )
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.put("/{user_id}", response_model=UserResponseModel)
def update_user(user_id: int, user: UserCreateModel):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET username = %s, master_password_hash = %s, email = %s WHERE user_id = %s",
            (user.username, user.master_password_hash, user.email, user_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
        
        # Fetch the updated user data
        cursor.execute("SELECT username, email, created_at FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        return UserResponseModel(
            user_id=user_id,
            username=user_data[0],
            email=user_data[1],
            created_at=user_data[2]
        )
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
        return {"detail": "User deleted successfully"}
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()
