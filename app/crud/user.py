from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.user import User
from app.models.bus import Bus
from app.schemas.user import UserCreate, DriverWithBusCreate, UserCreate as UserUpdate
from app.core.security import get_password_hash

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalars().first()

    async def get_by_phone(self, db: AsyncSession, *, phone: str) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.phone == phone))
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.username == username))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        # Check for existing user by email, phone, or username before creating
        existing_by_email = await self.get_by_email(db, email=obj_in.email)
        if existing_by_email:
            raise ValueError(f"User with email {obj_in.email} already exists.")
        
        existing_by_phone = await self.get_by_phone(db, phone=obj_in.phone)
        if existing_by_phone:
            raise ValueError(f"User with phone {obj_in.phone} already exists.")

        # Only check username if it's provided and not None
        if obj_in.username:
            existing_by_username = await self.get_by_username(db, username=obj_in.username)
            if existing_by_username:
                raise ValueError(f"User with username {obj_in.username} already exists.")

        db_obj = self.model(
            email=obj_in.email,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            password_hash=get_password_hash(obj_in.password),
            role=obj_in.role,
            username=obj_in.username # Ensure username is set
        )
        if obj_in.role == "driver" and hasattr(obj_in, 'license_number'):
            db_obj.license_number = obj_in.license_number
            db_obj.assigned_bus_id = obj_in.assigned_bus_id

        db.add(db_obj)
        # Removed await db.commit() - transaction management is now external
        await db.flush() # Use flush to get ID if needed for relationships before external commit
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
