from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserInDB

class BookingBase(BaseModel):
    trip_id: int
    seat_number: str

class BookingCreate(BookingBase):
    pass

class BookingInDB(BookingBase):
    id: int
    passenger_id: int
    is_boarded: bool
    is_paid: bool
    booked_at: datetime
    payment_ref: Optional[str] = None
    qr_token: Optional[str] = None

    class Config:
        from_attributes = True

class BookingWithQR(BookingInDB):
    qr_code_png_base64: Optional[str] = None

class PassengerBookingDetails(BookingInDB):
    passenger: UserInDB
