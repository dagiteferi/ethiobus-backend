from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, models, schemas
from app.core.database import get_db
from app.dependencies import get_current_passenger, get_current_user
from app.services import qr_service, payment_service

router = APIRouter()

@router.get("/trips/{trip_id}/details", response_model=schemas.trip.TripDetailsWithDriver)
async def get_trip_details_with_driver(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get detailed information about a trip, including public details of the driver and the bus.
    """
    trip = await crud.trip.get_with_driver_and_bus(db, trip_id=trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.get("/search", response_model=List[schemas.trip.TripDetailsWithDriver])
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

@router.get("/trip/{trip_id}", response_model=schemas.trip.TripDetails)
async def get_trip(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single trip by ID with bus and route details.
    """
    from sqlalchemy.future import select
    from sqlalchemy.orm import selectinload
    from app.models.trip import Trip
    
    result = await db.execute(
        select(Trip)
        .filter(Trip.id == trip_id)
        .options(selectinload(Trip.bus))
        .options(selectinload(Trip.route))
    )
    trip = result.scalars().first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")
    
    return trip

@router.post("/book", response_model=schemas.BookingWithQR)
async def book_trip(
    *,
    db: AsyncSession = Depends(get_db),
    booking_in: schemas.BookingCreate,
    payment_code: str = Query(..., description="Payment code for mock payment"),
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
            db, 
            trip_id=booking_in.trip_id, 
            passenger_id=current_passenger.id,
            seat_number=booking_in.seat_number
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

@router.get("/bookings", response_model=List[schemas.booking.BookingWithQR])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_passenger: models.User = Depends(get_current_passenger),
):
    """
    Get all bookings for the current passenger.
    """
    from sqlalchemy.future import select
    from sqlalchemy.orm import selectinload
    from app.models.booking import Booking
    
    result = await db.execute(
        select(Booking)
        .filter(Booking.passenger_id == current_passenger.id)
        .options(selectinload(Booking.trip).selectinload(models.Trip.bus))
        .options(selectinload(Booking.trip).selectinload(models.Trip.route))
        .order_by(Booking.booked_at.desc())
    )
    bookings_db = result.scalars().all()
    
    bookings_with_qr = []
    for booking in bookings_db:
        booking_schema = schemas.booking.BookingWithQR.model_validate(booking)
        if booking.qr_token:
            booking_schema.qr_code_png_base64 = qr_service.generate_qr_code_png_base64(booking.qr_token)
        bookings_with_qr.append(booking_schema)
        
    return bookings_with_qr

@router.get("/trips/{trip_id}/booked-seats", response_model=List[int])
async def get_booked_seats_for_trip(
    trip_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a list of booked seat numbers for a specific trip.
    """
    from sqlalchemy.future import select
    from app.models.booking import Booking

    result = await db.execute(
        select(Booking.seat_number)
        .filter(Booking.trip_id == trip_id)
        .filter(Booking.is_paid == True) # Only consider paid bookings as reserved
    )
    booked_seats = result.scalars().all()
    return booked_seats


