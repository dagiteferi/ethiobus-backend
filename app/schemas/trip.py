from pydantic import BaseModel
from datetime import datetime

from .bus import BusInDB, BusPublic
from .driver import DriverPublic
from .route import RouteInDB

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

class TripDetails(TripInDB):
    bus: BusInDB

class TripDetailsWithDriver(TripInDB):
    driver: DriverPublic
    bus: BusPublic
    route: RouteInDB

class TripUpdate(BaseModel):
    bus_id: int | None = None
    route_id: int | None = None
    driver_id: int | None = None
    departure_time: datetime | None = None
    arrival_time: datetime | None = None
    base_price_etb: float | None = None
    available_seats: int | None = None

