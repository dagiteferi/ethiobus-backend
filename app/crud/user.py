from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserCreate as UserUpdate  # Using UserCreate for update for now
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

user = CRUDUser(User)
