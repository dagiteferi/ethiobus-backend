from sqlalchemy import Column, Integer, String, Float, ForeignKey # Import ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.user import driver_route_association
from app.models.bus import Bus # Import Bus model

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    avg_duration_min = Column(Integer, nullable=False)

    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=True) # Add bus_id column
    bus = relationship("Bus", back_populates="routes") # Add bus relationship

    drivers = relationship("Driver", secondary=driver_route_association, back_populates="routes")
