from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripCreate as TripUpdate

class CRUDTrip(CRUDBase[Trip, TripCreate, TripUpdate]):
    async def get_multi_by_route(self, db: AsyncSession, *, route_id: int) -> List[Trip]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.route_id == route_id)
            .options(selectinload(self.model.bus))
        )
        return result.scalars().all()

trip = CRUDTrip(Trip)
