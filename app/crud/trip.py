from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripCreate as TripUpdate

class CRUDTrip(CRUDBase[Trip, TripCreate, TripUpdate]):
    async def get_with_driver_and_bus(self, db: AsyncSession, *, trip_id: int) -> Optional[Trip]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.id == trip_id)
            .options(
                joinedload(self.model.driver),
                joinedload(self.model.bus),
                joinedload(self.model.route)
            )
        )
        return result.scalars().first()

    async def get_multi_by_route(self, db: AsyncSession, *, route_id: int) -> List[Trip]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.route_id == route_id)
            .options(
                selectinload(self.model.bus),
                selectinload(self.model.driver),
                selectinload(self.model.route)
            )
        )
        return result.scalars().all()

    async def get_by_details(
        self,
        db: AsyncSession,
        *,
        bus_id: int,
        route_id: int,
        departure_time: datetime
    ) -> Optional[Trip]:
        result = await db.execute(
            select(self.model).filter(
                self.model.bus_id == bus_id,
                self.model.route_id == route_id,
                self.model.departure_time == departure_time,
            )
        )
        return result.scalars().first()

trip = CRUDTrip(Trip)
