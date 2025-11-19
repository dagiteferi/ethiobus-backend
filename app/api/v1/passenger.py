from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app import crud, models, schemas
from app.core.database import get_db
from app.dependencies import get_current_passenger
from app.services import qr_service, payment_service

router = APIRouter()

@router.get("/search", response_model=list[schemas.TripInDB])
async def search_trips(
    origin: str,
    dest: str,
    date: date,
    db: AsyncSession = Depends(get_db),
):
    """
    Search for trips based on origin, destination, and date.
    """
    result = await db.execute(
        select(models.Trip)
        .join(models.Route)
        .where(models.Route.origin == origin)
        .where(models.Route.destination == dest)
        .where(models.Trip.departure_time >= date)
    )
    trips = result.scalars().all()
    return trips

@router.post("/book", response_model=schemas.BookingWithQR)
async def book_trip(
    *,
    db: AsyncSession = Depends(get_db),
    booking_in: schemas.BookingCreate,
    payment_code: str, # This would be part of a larger payment object in reality
    current_passenger: models.Passenger = Depends(get_current_passenger),
):
    """
    Book a trip for the current passenger.
    """
    trip = await crud.trip.get(db, id=booking_in.trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.available_seats <= 0:
        raise HTTPException(status_code=400, detail="No available seats")

    # Mock payment processing
    payment_ref = payment_service.process_mock_payment(payment_code)

    # Create booking
    booking = await crud.booking.create(db, obj_in=booking_in)
    booking.passenger_id = current_passenger.id
    booking.is_paid = True
    booking.payment_ref = payment_ref
    
    # Generate QR token and code
    qr_token = qr_service.create_qr_token(schemas.BookingInDB.model_validate(booking))
    booking.qr_token = qr_token
    
    await db.commit()
    await db.refresh(booking)

    # Decrement available seats
    trip.available_seats -= 1
    await db.commit()

    # Prepare response
    booking_response = schemas.BookingWithQR.model_validate(booking)
    booking_response.qr_code_png_base64 = qr_service.generate_qr_code_png_base64(qr_token)
    
    return booking_response
