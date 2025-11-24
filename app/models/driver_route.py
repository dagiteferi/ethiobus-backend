from sqlalchemy import Column, Integer, ForeignKey
from app.models.base import Base

class DriverRoute(Base):
    __tablename__ = "driver_routes"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
