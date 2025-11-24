from pydantic import BaseModel
from typing import Optional

class RouteBase(BaseModel):
    origin: str
    destination: str
    distance_km: float
    avg_duration_min: int
    bus_id: Optional[int] = None # Add optional bus_id

class RouteCreate(RouteBase):
    pass

class RouteUpdate(RouteBase): # Define RouteUpdate
    origin: Optional[str] = None
    destination: Optional[str] = None
    distance_km: Optional[float] = None
    avg_duration_min: Optional[int] = None
    bus_id: Optional[int] = None

class RouteInDB(RouteBase):
    id: int
    # bus: Optional[BusInDB] = None # Assuming BusInDB exists and we want to embed bus details

    class Config:
        from_attributes = True
