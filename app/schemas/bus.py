from pydantic import BaseModel
from typing import Optional

class BusBase(BaseModel):
    plate_number: str
    model: str
    total_seats: int
    status: str = "active"

class BusCreate(BusBase):
    pass

class BusUpdate(BusBase):
    plate_number: Optional[str] = None
    model: Optional[str] = None
    total_seats: Optional[int] = None
    status: Optional[str] = None

class BusInDB(BusBase):
    id: int

    class Config:
        from_attributes = True
