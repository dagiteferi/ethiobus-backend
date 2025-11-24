from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi import HTTPException # Import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.bus import Bus
from app.models.trip import Trip # Import Trip model
from app.schemas.bus import BusCreate, BusUpdate

class CRUDBus(CRUDBase[Bus, BusCreate, BusUpdate]):
    async def get_by_plate_number(self, db: AsyncSession, *, plate_number: str) -> Optional[Bus]:
        result = await db.execute(select(self.model).filter(self.model.plate_number == plate_number))
        return result.scalars().first()

    async def remove(self, db: AsyncSession, *, id: int) -> Bus: # Override remove method
        bus = await self.get(db, id)
        if not bus:
            raise HTTPException(status_code=404, detail="Bus not found")

        # Check for associated trips
        trips_count_result = await db.execute(
            select(Trip).filter(Trip.bus_id == id)
        )
        trips_count = trips_count_result.scalars().first()
        if trips_count:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete bus: it has associated trips. Please reassign or delete trips first."
            )
        
        # Check for associated drivers (optional, but good for integrity)
        # Assuming Driver model has a bus_id foreign key
        # drivers_count_result = await db.execute(
        #     select(Driver).filter(Driver.assigned_bus_id == id)
        # )
        # drivers_count = drivers_count_result.scalars().first()
        # if drivers_count:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Cannot delete bus: it has assigned drivers. Please reassign drivers first."
        #     )

        await db.delete(bus)
        await db.flush()
        return bus

bus = CRUDBus(Bus)
