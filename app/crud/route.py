from typing import Any, Dict, Optional, Union
from fastapi import HTTPException # Import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.route import Route
from app.models.bus import Bus # Import Bus model
from app.schemas.route import RouteCreate, RouteUpdate

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

    async def create(self, db: AsyncSession, *, obj_in: RouteCreate) -> Route:
        if obj_in.bus_id:
            # Check if the bus is already assigned to another route
            existing_route_with_bus = await db.execute(
                select(Route).filter(Route.bus_id == obj_in.bus_id)
            )
            if existing_route_with_bus.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail=f"Bus with ID {obj_in.bus_id} is already assigned to another route."
                )
            # Check if bus exists
            bus = await db.execute(select(Bus).filter(Bus.id == obj_in.bus_id))
            if not bus.scalars().first():
                raise HTTPException(status_code=404, detail=f"Bus with ID {obj_in.bus_id} not found.")

        return await super().create(db, obj_in=obj_in)

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Route,
        obj_in: Union[RouteUpdate, Dict[str, Any]]
    ) -> Route:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "bus_id" in update_data and update_data["bus_id"] is not None:
            bus_id = update_data["bus_id"]
            # Check if the bus is already assigned to another route (excluding the current route being updated)
            existing_route_with_bus = await db.execute(
                select(Route).filter(Route.bus_id == bus_id, Route.id != db_obj.id)
            )
            if existing_route_with_bus.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail=f"Bus with ID {bus_id} is already assigned to another route."
                )
            # Check if bus exists
            bus = await db.execute(select(Bus).filter(Bus.id == bus_id))
            if not bus.scalars().first():
                raise HTTPException(status_code=404, detail=f"Bus with ID {bus_id} not found.")
        
        return await super().update(db, db_obj=db_obj, obj_in=obj_in)

route = CRUDRoute(Route)
