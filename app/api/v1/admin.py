from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core.database import get_db
from app.dependencies import get_current_admin
from app.schemas.user import DriverCreate, DriverWithBusCreate
from app.schemas.bus import BusCreate
from app.schemas.route import RouteCreate

router = APIRouter()

@router.post("/bus", response_model=schemas.BusInDB)
async def create_bus(
    *,
    db: AsyncSession = Depends(get_db),
    bus_in: BusCreate,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Create a new bus.
    """
    bus = await crud.bus.create(db, obj_in=bus_in)
    return bus

@router.post("/route", response_model=schemas.RouteInDB)
async def create_route(
    *,
    db: AsyncSession = Depends(get_db),
    route_in: RouteCreate,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Create a new route.
    """
    route = await crud.route.create(db, obj_in=route_in)
    return route

@router.post("/driver", response_model=schemas.UserInDB)
async def create_driver(
    *,
    db: AsyncSession = Depends(get_db),
    driver_in: DriverCreate,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Create a new driver and assign them to an existing bus.
    """
    user = await crud.user.get_by_username(db, username=driver_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    driver = await crud.user.create(db, obj_in=driver_in)
    return driver

@router.post("/driver-with-bus", response_model=schemas.UserInDB)
async def create_driver_and_bus(
    *,
    db: AsyncSession = Depends(get_db),
    driver_bus_in: DriverWithBusCreate,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Create a new driver and their bus simultaneously.
    """
    user = await crud.user.get_by_username(db, username=driver_bus_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    bus = await crud.bus.get_by_plate_number(db, plate_number=driver_bus_in.plate_number)
    if bus:
        raise HTTPException(
            status_code=400,
            detail="A bus with this plate number already exists.",
        )

    driver = await crud.user.create_driver_with_bus(db, obj_in=driver_bus_in)
    return driver
