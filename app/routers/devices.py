from fastapi import APIRouter, HTTPException, status
from app.db import get_connection
from app.models.devices import DeviceCreate, DeviceResponse, DeviceUpdate 
from app.models.users import UserResponseModel
from datetime import datetime
from typing import List
import mysql.connector

router = APIRouter(prefix="/devices", tags=["devices"])




@router.get("/", response_model=List[DeviceResponse])
def get_devices():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT device_id, user_id, device_type, brand, model, serial_number, operating_system, admin_password_encrypted, purchase_date, notes, created_at FROM devices")
        devices = cursor.fetchall()
        return [
            DeviceResponse(
                device_id=device[0],
                user_id=device[1],
                device_type=device[2],
                brand=device[3],
                model=device[4],
                serial_number=device[5],
                operating_system=device[6],
                admin_password_encrypted=device[7],
                purchase_date=device[8],
                notes=device[9],
                created_at=device[10]
            ) for device in devices
        ]
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(device_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT device_id, user_id, device_type, brand, model, serial_number, operating_system, admin_password_encrypted, purchase_date, notes, created_at FROM devices WHERE device_id = %s", (device_id,))
        device = cursor.fetchone()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return DeviceResponse(
            device_id=device[0],
            user_id=device[1],
            device_type=device[2],
            brand=device[3],
            model=device[4],
            serial_number=device[5],
            operating_system=device[6],
            admin_password_encrypted=device[7],
            purchase_date=device[8],
            notes=device[9],
            created_at=device[10]
        )
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(device: DeviceCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO devices (user_id, device_type, brand, model, serial_number, operating_system, admin_password_encrypted, purchase_date, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                device.user_id,
                device.device_type,
                device.brand,
                device.model,
                device.serial_number,
                device.operating_system,
                device.admin_password_encrypted,
                device.purchase_date,
                device.notes
            )
        )
        conn.commit()
        device_id = cursor.lastrowid
        return get_device(device_id)
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(device_id: int, device_update: DeviceUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE devices SET device_type = %s, brand = %s, model = %s, serial_number = %s, operating_system = %s, admin_password_encrypted = %s, purchase_date = %s, notes = %s WHERE device_id = %s",
            (
                device_update.device_type,
                device_update.brand,
                device_update.model,
                device_update.serial_number,
                device_update.operating_system,
                device_update.admin_password_encrypted,
                device_update.purchase_date,
                device_update.notes,
                device_id
            )
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        conn.commit()
        return get_device(device_id)
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()


@router.delete("/{device_id}", status_code=status.HTTP_200_OK)
def delete_device(device_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM devices WHERE device_id = %s", (device_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device not found")
        conn.commit()
        return {"detail": "Device deleted successfully"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()