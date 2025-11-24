from pydantic import BaseModel
from typing import List, Optional
from app.schemas.user import UserInDB
from app.schemas.route import RouteInDB

class DriverRouteAssignment(BaseModel):
    driver_id: int
    route_ids: List[int]

class PassengerForDriver(BaseModel):
    full_name: str
    seat_number: str
    is_boarded: bool

    class Config:
        from_attributes = True

class TripPassengers(BaseModel):
    trip_id: int
    passengers: List[PassengerForDriver]
