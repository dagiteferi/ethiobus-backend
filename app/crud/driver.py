from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import Driver
from app.models.route import Route
from app.models.driver_route import DriverRoute

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
