from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.base import Base
import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    seat_number = Column(String, nullable=False)
    qr_token = Column(String, unique=True, nullable=True)
    is_boarded = Column(Boolean, default=False, nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    booked_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    payment_ref = Column(String, nullable=True)

    passenger = relationship("Passenger", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")
