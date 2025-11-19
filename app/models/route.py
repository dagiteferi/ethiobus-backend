from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance_km = Column(Float, nullable=False)
    avg_duration_min = Column(Integer, nullable=False)
