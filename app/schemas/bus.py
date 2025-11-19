from pydantic import BaseModel

class BusBase(BaseModel):
    plate_number: str
    model: str
    total_seats: int
    status: str = "active"

class BusCreate(BusBase):
    pass

class BusInDB(BusBase):
    id: int

    class Config:
        from_attributes = True
