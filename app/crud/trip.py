from app.crud.base import CRUDBase
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripCreate as TripUpdate

class CRUDTrip(CRUDBase[Trip, TripCreate, TripUpdate]):
    pass

trip = CRUDTrip(Trip)
