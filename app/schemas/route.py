from pydantic import BaseModel

class RouteBase(BaseModel):
    origin: str
    destination: str
    distance_km: float
    avg_duration_min: int

class RouteCreate(RouteBase):
    pass

class RouteInDB(RouteBase):
    id: int

    class Config:
        from_attributes = True
