from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.route import Route
from app.schemas.route import RouteCreate, RouteCreate as RouteUpdate

class CRUDRoute(CRUDBase[Route, RouteCreate, RouteUpdate]):
    async def get_by_source_and_destination(
        self, db: AsyncSession, *, source: str, destination: str
    ) -> Optional[Route]:
        result = await db.execute(
            select(self.model).filter(
                func.lower(self.model.origin) == source.lower(),
                func.lower(self.model.destination) == destination.lower(),
            )
        )
        return result.scalars().first()

route = CRUDRoute(Route)
