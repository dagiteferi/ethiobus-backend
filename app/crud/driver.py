from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.user import User, Driver # Import User and Driver
from app.models.bus import Bus # Import Bus
from app.models.route import Route
from app.models.driver_route import DriverRoute
from app.schemas.user import DriverCreate, DriverUpdate # Import DriverCreate and DriverUpdate
from app.core import security # Import security for password hashing

class CRUDDriver(CRUDBase[Driver, DriverCreate, DriverUpdate]):
    async def get_by_license_number(self, db: AsyncSession, *, license_number: str) -> Optional[Driver]:
        result = await db.execute(select(self.model).filter(self.model.license_number == license_number))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: DriverCreate) -> Driver:
        # Hash password
        hashed_password = security.get_password_hash(obj_in.password)
        db_obj = Driver(
            email=obj_in.email,
            username=obj_in.username,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            password_hash=hashed_password,
            role="driver",
            license_number=obj_in.license_number,
            assigned_bus_id=obj_in.assigned_bus_id,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Driver,
        obj_in: Union[DriverUpdate, Dict[str, Any]]
    ) -> Driver:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["password_hash"] = security.get_password_hash(update_data["password"])
            del update_data["password"] # Remove plain password

        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Driver:
        driver = await self.get(db, id)
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        # Check for associated trips
        from app.models.trip import Trip # Import Trip model here to avoid circular dependency
        trips_count_result = await db.execute(
            select(Trip).filter(Trip.driver_id == id)
        )
        trips_count = trips_count_result.scalars().first()
        if trips_count:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete driver: they have associated trips. Please reassign or delete trips first."
            )

        # Clear assigned bus
        if driver.assigned_bus_id:
            driver.assigned_bus_id = None
            db.add(driver)
            await db.flush()

        # Clear assigned routes
        await db.execute(DriverRoute.__table__.delete().where(DriverRoute.driver_id == id))
        await db.flush()

        await db.delete(driver)
        await db.flush()
        return driver

async def assign_routes_to_driver(db: AsyncSession, *, driver_id: int, route_ids: List[int]) -> Driver:
    """
    Assign routes to a driver.
    """
    driver = await db.get(Driver, driver_id)
    if not driver:
        return None

    # Clear existing routes
    await db.execute(DriverRoute.__table__.delete().where(DriverRoute.driver_id == driver_id))

    for route_id in route_ids:
        route = await db.get(Route, route_id)
        if route:
            driver_route = DriverRoute(driver_id=driver_id, route_id=route_id)
            db.add(driver_route)

    await db.commit()
    await db.refresh(driver)
    return driver

from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.user import Driver
from app.schemas.user import DriverCreate, DriverUpdate
from app.core.security import get_password_hash

class CRUDDriver(CRUDBase[Driver, DriverCreate, DriverUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: DriverCreate) -> Driver:
        db_obj = self.model(
            email=obj_in.email,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            password_hash=get_password_hash(obj_in.password),
            role="driver",
            username=obj_in.username,
            license_number=obj_in.license_number,
            assigned_bus_id=obj_in.assigned_bus_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

driver = CRUDDriver(Driver)

