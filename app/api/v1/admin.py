from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core.database import get_db
from app.dependencies import get_current_admin
from app.schemas.user import DriverCreate, DriverWithBusCreate
from app.schemas.bus import BusCreate
from app.schemas.route import RouteCreate
from app.schemas.driver import DriverRouteAssignment

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
    try:
        bus = await crud.bus.create(db, obj_in=bus_in)
        return bus
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="A bus with this plate number already exists.",
        )

@router.get("/bus", response_model=list[schemas.BusInDB])
async def read_buses(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Retrieve multiple buses.
    """
    buses = await crud.bus.get_multi(db, skip=skip, limit=limit)
    return buses

@router.get("/bus/{bus_id}", response_model=schemas.BusInDB)
async def read_bus_by_id(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Retrieve a single bus by ID.
    """
    bus = await crud.bus.get(db, id=bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus

@router.put("/bus/{bus_id}", response_model=schemas.BusInDB)
async def update_bus(
    *,
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    bus_in: schemas.BusUpdate,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Update an existing bus.
    """
    bus = await crud.bus.get(db, id=bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    try:
        bus = await crud.bus.update(db, db_obj=bus, obj_in=bus_in)
        return bus
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="A bus with this plate number already exists.",
        )

@router.delete("/bus/{bus_id}", response_model=schemas.BusInDB)
async def delete_bus(
    *,
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Delete a bus.
    """
    bus = await crud.bus.get(db, id=bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    bus = await crud.bus.remove(db, id=bus_id)
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

@router.post("/driver/assign-routes", response_model=schemas.UserInDB)
async def assign_routes_to_driver(
    *,
    db: AsyncSession = Depends(get_db),
    assignment: DriverRouteAssignment,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Assign routes to a driver.
    """
    driver = await crud.driver.assign_routes_to_driver(
        db, driver_id=assignment.driver_id, route_ids=assignment.route_ids
    )
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver
