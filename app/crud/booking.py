from app.crud.base import CRUDBase
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingCreate as BookingUpdate

class CRUDBooking(CRUDBase[Booking, BookingCreate, BookingUpdate]):
    pass

booking = CRUDBooking(Booking)
