from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    role = Column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": role,
    }

class Passenger(User):
    __mapper_args__ = {
        "polymorphic_identity": "passenger",
    }
    bookings = relationship("Booking", back_populates="passenger")

class Driver(User):
    license_number = Column(String, unique=True, nullable=True)
    assigned_bus_id = Column(Integer, ForeignKey("buses.id"), nullable=True)
    
    assigned_bus = relationship("Bus", back_populates="drivers")
    trips = relationship("Trip", back_populates="driver")

    __mapper_args__ = {
        "polymorphic_identity": "driver",
    }

class Admin(User):
    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }
