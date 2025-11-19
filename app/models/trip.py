from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.base import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    base_price_etb = Column(Float, nullable=False)
    available_seats = Column(Integer, nullable=False)

    bus = relationship("Bus", back_populates="trips")
    route = relationship("Route")
    driver = relationship("Driver", back_populates="trips")
    bookings = relationship("Booking", back_populates="trip")
