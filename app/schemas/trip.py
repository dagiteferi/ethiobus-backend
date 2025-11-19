from pydantic import BaseModel
from datetime import datetime

class TripBase(BaseModel):
    bus_id: int
    route_id: int
    driver_id: int
    departure_time: datetime
    arrival_time: datetime
    base_price_etb: float
    available_seats: int

class TripCreate(TripBase):
    pass

class TripInDB(TripBase):
    id: int

    class Config:
        from_attributes = True
