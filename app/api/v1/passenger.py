from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, models, schemas
from app.core.database import get_db
from app.dependencies import get_current_passenger
from app.services import qr_service, payment_service

router = APIRouter()

@router.get("/search", response_model=List[schemas.trip.TripDetails])
async def search_trips(
    source: str,
    destination: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Search for available trips by source and destination.
    Returns trip details along with the associated bus information.
    """
    route = await crud.route.get_by_source_and_destination(
        db, source=source, destination=destination
    )
    if not route:
        return []
    
    trips = await crud.trip.get_multi_by_route(db, route_id=route.id)
    return trips

@router.post("/book", response_model=schemas.BookingWithQR)
async def book_trip(
    *,
    db: AsyncSession = Depends(get_db),
    booking_in: schemas.BookingCreate, # This schema only needs trip_id
    payment_code: str, # This would be part of a larger payment object in reality
    current_passenger: models.User = Depends(get_current_passenger),
):
    """
    Book a trip for the current passenger.
    """
    # Mock payment processing
    payment_ref = payment_service.process_mock_payment(payment_code)

    try:
        # Use the new atomic CRUD function
        booking = await crud.booking.create_with_seat_check(
            db, trip_id=booking_in.trip_id, passenger_id=current_passenger.id
        )
    except ValueError as e:
        # Convert specific ValueErrors from CRUD to HTTPExceptions
        if "Trip not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "No available seats" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="An unexpected error occurred during booking.")

    # Update booking details after creation
    booking.is_paid = True
    booking.payment_ref = payment_ref
    
    # Generate QR token and code
    qr_token = qr_service.create_qr_token(schemas.BookingInDB.model_validate(booking))
    booking.qr_token = qr_token
    
    db.add(booking) # Add updated booking object to session
    await db.commit()
    await db.refresh(booking)

    # Prepare response
    booking_response = schemas.BookingWithQR.model_validate(booking)
    booking_response.qr_code_png_base64 = qr_service.generate_qr_code_png_base64(qr_token)
    
    return booking_response

