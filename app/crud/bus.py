from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.bus import Bus
from app.schemas.bus import BusCreate, BusCreate as BusUpdate

class CRUDBus(CRUDBase[Bus, BusCreate, BusUpdate]):
    async def get_by_plate_number(self, db: AsyncSession, *, plate_number: str) -> Optional[Bus]:
        result = await db.execute(select(self.model).filter(self.model.plate_number == plate_number))
        return result.scalars().first()

bus = CRUDBus(Bus)
