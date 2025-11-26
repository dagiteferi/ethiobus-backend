from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import date
import cv2
import numpy as np
from typing import List

from app import crud, models, schemas
from app.core.database import get_db
from app.dependencies import get_current_driver
from app.services import qr_service

router = APIRouter()

@router.get("/trips", response_model=List[schemas.trip.TripDetailsWithDriver])
async def get_driver_trips(
    db: AsyncSession = Depends(get_db),
    current_driver: models.User = Depends(get_current_driver),
):
    """
    Get all trips for the current driver for today.
    """
    result = await db.execute(
        select(models.Trip)
        .where(models.Trip.driver_id == current_driver.id)
        .options(
            selectinload(models.Trip.route),
            selectinload(models.Trip.bus),
            selectinload(models.Trip.driver)
        )
    )
    trips = result.scalars().all()
    return trips

@router.get("/passengers", response_model=list[schemas.UserInDB])
async def get_todays_passengers(
    db: AsyncSession = Depends(get_db),
    current_driver: models.User = Depends(get_current_driver),
):
    """
    Get the list of passengers for the driver's current trip.
    """
    # Find the driver's trip for today
    result = await db.execute(
        select(models.Trip)
        .where(models.Trip.driver_id == current_driver.id)
        .where(func.date(models.Trip.departure_time) == date.today())
    )
    trip = result.scalars().first()

    if not trip:
        raise HTTPException(status_code=404, detail="No trip assigned for today.")

    # Get passengers for that trip
    result = await db.execute(
        select(models.User)
        .join(models.Booking)
        .where(models.Booking.trip_id == trip.id)
    )
    passengers = result.scalars().all()
    return passengers

@router.get("/trips/{trip_id}/passengers", response_model=List[schemas.booking.PassengerBookingDetails])
async def get_passengers_for_trip(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
    current_driver: models.User = Depends(get_current_driver),
):
    """
    Get the list of passengers for a specific trip assigned to the current driver.
    """
    # Authorization: Check if the trip belongs to the current driver
    trip = await crud.trip.get(db, id=trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")
    if trip.driver_id != current_driver.id:
        raise HTTPException(status_code=403, detail="You are not authorized to view passengers for this trip.")

    bookings = await crud.booking.get_multi_by_trip_id(db, trip_id=trip_id)
    return bookings

@router.post("/scan")
async def scan_qr_code(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_driver: models.User = Depends(get_current_driver),
):
    """
    Scan a passenger's QR code to mark them as boarded.
    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(img)

    if not data:
        raise HTTPException(status_code=400, detail="Could not decode QR code.")

    payload = qr_service.verify_qr_token(data)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid QR code token.")

    booking_id = payload.get("booking_id")
    booking = await crud.booking.get(db, id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Check if the booking belongs to one of the driver's trips for today
    result = await db.execute(
        select(models.Trip)
        .where(models.Trip.driver_id == current_driver.id)
        .where(models.Trip.id == booking.trip_id)
        .where(func.date(models.Trip.departure_time) == date.today())
    )
    trip = result.scalars().first()
    
    if not trip:
        raise HTTPException(status_code=403, detail="Booking is not for one of your trips today.")

    booking.is_boarded = True
    await db.commit()

    return {"status": "success", "detail": f"Passenger for booking {booking_id} boarded."}

@router.post("/scan-token")
async def scan_qr_token(
    request: dict,
    db: AsyncSession = Depends(get_db),
    current_driver: models.User = Depends(get_current_driver),
):
    """
    Scan a passenger's QR code token (when already decoded from QR scanner).
    """
    qr_token = request.get("qr_token")
    if not qr_token:
        raise HTTPException(status_code=400, detail="QR token is required.")
    
    payload = qr_service.verify_qr_token(qr_token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid QR code token.")

    booking_id = payload.get("booking_id")
    booking = await crud.booking.get(db, id=booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not. found.")

    # Check if the booking belongs to one of the driver's trips for today
    result = await db.execute(
        select(models.Trip)
        .where(models.Trip.driver_id == current_driver.id)
        .where(models.Trip.id == booking.trip_id)
        .where(func.date(models.Trip.departure_time) == date.today())
    )
    trip = result.scalars().first()
    
    if not trip:
        raise HTTPException(status_code=403, detail="Booking is not for one of your trips today.")

    booking.is_boarded = True
    await db.commit()

    return {"status": "success", "detail": f"Passenger for booking {booking_id} boarded."}
