from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, nullable=False)
    model = Column(String, nullable=False)
    total_seats = Column(Integer, nullable=False)
    status = Column(String, default="active", nullable=False) # active | maintenance

    drivers = relationship("Driver", back_populates="assigned_bus")
    trips = relationship("Trip", back_populates="bus")
    routes = relationship("Route", back_populates="bus") # Add routes relationship
