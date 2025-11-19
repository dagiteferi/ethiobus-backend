from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.user import User
from app.models.bus import Bus
from app.schemas.user import UserCreate, DriverWithBusCreate, UserCreate as UserUpdate
from app.core.security import get_password_hash

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.username == username))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            username=obj_in.username,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            password_hash=get_password_hash(obj_in.password),
            role=obj_in.role,
        )
        if obj_in.role == "driver" and hasattr(obj_in, 'license_number'):
            db_obj.license_number = obj_in.license_number
            db_obj.assigned_bus_id = obj_in.assigned_bus_id

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_driver_with_bus(self, db: AsyncSession, *, obj_in: DriverWithBusCreate) -> User:
        """
        Create a new driver and a new bus for them in a single transaction.
        """
        # Create the bus object
        bus_obj = Bus(
            plate_number=obj_in.plate_number,
            model=obj_in.model,
            total_seats=obj_in.total_seats,
        )
        db.add(bus_obj)
        await db.flush()  # Flush to get the bus_obj.id before committing

        # Create the driver object
        driver_obj = self.model(
            username=obj_in.username,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            password_hash=get_password_hash(obj_in.password),
            role="driver",
            license_number=obj_in.license_number,
            assigned_bus_id=bus_obj.id,
        )
        db.add(driver_obj)
        await db.commit()
        await db.refresh(driver_obj)
        return driver_obj

user = CRUDUser(User)
