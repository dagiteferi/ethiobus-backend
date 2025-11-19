from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.booking import Booking
from app.models.trip import Trip
from app.schemas.booking import BookingCreate, BookingCreate as BookingUpdate


class CRUDBooking(CRUDBase[Booking, BookingCreate, BookingUpdate]):
    async def create_with_seat_check(
        self, db: AsyncSession, *, trip_id: int, passenger_id: int
    ) -> Booking:
        """
        Creates a booking after atomically checking for and decrementing available seats.
        Raises ValueError if trip is not found or no seats are available.
        """
        # Lock the trip row for the duration of the transaction
        trip = await db.get(Trip, trip_id, with_for_update=True)

        if not trip:
            raise ValueError("Trip not found")
        
        if trip.available_seats <= 0:
            raise ValueError("No available seats on this trip")

        # Decrement seat count
        trip.available_seats -= 1

        # Create booking object
        db_obj = self.model(trip_id=trip_id, passenger_id=passenger_id)
        
        db.add(trip)
        db.add(db_obj)
        
        await db.flush()
        return db_obj

    async def get_multi_by_trip_id(self, db: AsyncSession, *, trip_id: int) -> List[Booking]:
        """
        Retrieves all bookings for a given trip ID, eager loading passenger details.
        """
        result = await db.execute(
            select(self.model)
            .filter(self.model.trip_id == trip_id)
            .options(selectinload(self.model.passenger))
        )
        return result.scalars().all()

booking = CRUDBooking(Booking)
