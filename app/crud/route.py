from app.crud.base import CRUDBase
from app.models.route import Route
from app.schemas.route import RouteCreate, RouteCreate as RouteUpdate

class CRUDRoute(CRUDBase[Route, RouteCreate, RouteUpdate]):
    pass

route = CRUDRoute(Route)
