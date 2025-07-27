from fastapi import APIRouter, HTTPException, status
from app.db import get_connection
from app.models.credit_cards import CreditCardCreateRequest,CreditCardCreateDB, CreditCardResponse
from app.models.users import UserResponseModel

from datetime import datetime
from typing import List
import mysql.connector



router = APIRouter(prefix="/credit_cards", tags=["credit_cards"])
@router.get("/", response_model=List[CreditCardResponse])
def get_credit_cards():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT card_id, user_id, card_holder_name, card_number_encrypted, expiration_date, cvv_encrypted, billing_address, card_type, created_at FROM credit_cards")
        credit_cards = cursor.fetchall()
        return [
            CreditCardResponse(
                card_id=cc[0],
                user_id=cc[1],
                card_holder_name=cc[2],
                card_number_encrypted=cc[3],
                expiration_date=cc[4],
                cvv_encrypted=cc[5],
                billing_address=cc[6],
                card_type=cc[7],
                created_at=cc[8]
            ) for cc in credit_cards
        ]
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()


@router.get("/{card_id}", response_model=CreditCardResponse)
def get_credit_card(card_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT card_id, user_id, card_holder_name, card_number_encrypted, expiration_date, cvv_encrypted, billing_address, card_type, created_at FROM credit_cards WHERE card_id = %s", (card_id,))
        credit_card = cursor.fetchone()
        if not credit_card:
            raise HTTPException(status_code=404, detail="Credit card not found")
        return CreditCardResponse(
            card_id=credit_card[0],
            user_id=credit_card[1],
            card_holder_name=credit_card[2],
            card_number_encrypted=credit_card[3],
            expiration_date=credit_card[4],
            cvv_encrypted=credit_card[5],
            billing_address=credit_card[6],
            card_type=credit_card[7],
            created_at=credit_card[8]
        )
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=CreditCardResponse, status_code=status.HTTP_201_CREATED)
def create_credit_card(card: CreditCardCreateRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Convert request to DB model (in a real app, you would encrypt here)
        db_card = {
            'user_id': card.user_id,
            'card_number_encrypted': card.card_number,  # In production, encrypt this
            'cvv_encrypted': card.cvv,                 # In production, encrypt this
            'card_holder_name': card.card_holder_name,
            'expiration_date': card.expiration_date,
            'billing_address': card.billing_address,
            'card_type': card.card_type
        }

        cursor.execute(
            """INSERT INTO credit_cards 
            (user_id, card_holder_name, card_number_encrypted, 
             expiration_date, cvv_encrypted, billing_address, card_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (db_card['user_id'], db_card['card_holder_name'], db_card['card_number_encrypted'],
             db_card['expiration_date'], db_card['cvv_encrypted'], 
             db_card['billing_address'], db_card['card_type'])
        )
        conn.commit()
        card_id = cursor.lastrowid
        
        # Fetch the newly created card (without sensitive data)
        cursor.execute(
            """SELECT card_id, user_id, card_holder_name, 
                      expiration_date, billing_address, card_type, created_at 
               FROM credit_cards WHERE card_id = %s""",
            (card_id,)
        )
        new_card = cursor.fetchone()
        
        return CreditCardResponse(
            card_id=new_card[0],
            user_id=new_card[1],
            card_holder_name=new_card[2],
            expiration_date=new_card[3],
            billing_address=new_card[4],
            card_type=new_card[5],
            created_at=new_card[6]
        )
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()


@router.put("/{card_id}", response_model=CreditCardResponse)
def update_credit_card(card_id: int, card: CreditCardCreateRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # First verify the card exists
        cursor.execute("SELECT 1 FROM credit_cards WHERE card_id = %s", (card_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Credit card not found")

        # Update the card
        cursor.execute(
            """UPDATE credit_cards 
               SET user_id = %s, card_holder_name = %s, 
                   card_number_encrypted = %s, expiration_date = %s, 
                   cvv_encrypted = %s, billing_address = %s, 
                   card_type = %s 
               WHERE card_id = %s""",
            (card.user_id, card.card_holder_name, card.card_number,
             card.expiration_date, card.cvv, card.billing_address,
             card.card_type, card_id)
        )
        conn.commit()

        # Fetch the updated card
        cursor.execute(
            """SELECT card_id, user_id, card_holder_name, 
                      expiration_date, billing_address, card_type, created_at 
               FROM credit_cards WHERE card_id = %s""",
            (card_id,)
        )
        updated_card = cursor.fetchone()

        return CreditCardResponse(
            card_id=updated_card[0],
            user_id=updated_card[1],
            card_holder_name=updated_card[2],
            expiration_date=updated_card[3],
            billing_address=updated_card[4],
            card_type=updated_card[5],
            created_at=updated_card[6]
        )
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()


@router.delete("/{card_id}", status_code=status.HTTP_200_OK)
def delete_credit_card(card_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM credit_cards WHERE card_id = %s", (card_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Credit card not found")
        conn.commit()
        return {"detail": "Credit card deleted successfully"}
    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()