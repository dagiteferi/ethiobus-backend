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

@router.get("/route", response_model=list[schemas.RouteInDB])
async def read_routes(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Retrieve multiple routes.
    """
    routes = await crud.route.get_multi(db, skip=skip, limit=limit)
    return routes

@router.post("/route", response_model=schemas.RouteInDB)
async def create_route(
    *,
    db: AsyncSession = Depends(get_db),
    route_in: schemas.RouteCreate, # Use schemas.RouteCreate
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Create a new route.
    """
    try:
        route = await crud.route.create(db, obj_in=route_in)
        return route
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="A route with this origin and destination already exists.",
        )

@router.get("/route/{route_id}", response_model=schemas.RouteInDB)
async def read_route_by_id(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Retrieve a single route by ID.
    """
    route = await crud.route.get(db, id=route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

@router.put("/route/{route_id}", response_model=schemas.RouteInDB)
async def update_route(
    *,
    route_id: int,
    db: AsyncSession = Depends(get_db),
    route_in: schemas.RouteUpdate, # Use schemas.RouteUpdate
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Update an existing route.
    """
    route = await crud.route.get(db, id=route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    try:
        route = await crud.route.update(db, db_obj=route, obj_in=route_in)
        return route
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="A route with this origin and destination already exists.",
        )

@router.delete("/route/{route_id}", response_model=schemas.RouteInDB)
async def delete_route(
    *,
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Delete a route.
    """
    route = await crud.route.get(db, id=route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    route = await crud.route.remove(db, id=route_id)
    return route

@router.get("/driver", response_model=list[schemas.UserInDB])
async def read_drivers(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Retrieve multiple drivers.
    """
    drivers = await crud.driver.get_multi(db, skip=skip, limit=limit)
    return drivers

@router.post("/driver", response_model=schemas.UserInDB)
async def create_driver(
    *,
    db: AsyncSession = Depends(get_db),
    driver_in: schemas.DriverCreate,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Create a new driver.
    """
    # Check for existing user by email (email is unique)
    user_by_email = await crud.user.get_by_email(db, email=driver_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Check for existing driver by license number (license number is unique for drivers)
    existing_driver_by_license = await crud.driver.get_by_license_number(db, license_number=driver_in.license_number)
    if existing_driver_by_license:
        raise HTTPException(
            status_code=400,
            detail="A driver with this license number already exists.",
        )

    # Check for existing user by username if provided and not empty
    if driver_in.username:
        user_by_username = await crud.user.get_by_username(db, username=driver_in.username)
        if user_by_username:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )

    try:
        driver = await crud.driver.create(db, obj_in=driver_in)
        return driver
    except IntegrityError:
        # This catch is a fallback, as specific checks are done above
        raise HTTPException(
            status_code=400,
            detail="An unexpected database integrity error occurred (e.g., duplicate email or license number).",
        )

@router.get("/driver/{driver_id}", response_model=schemas.UserInDB)
async def read_driver_by_id(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Retrieve a single driver by ID.
    """
    driver = await crud.driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

@router.put("/driver/{driver_id}", response_model=schemas.UserInDB)
async def update_driver(
    *,
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    driver_in: schemas.DriverUpdate,
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Update an existing driver.
    """
    driver = await crud.driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    try:
        driver = await crud.driver.update(db, db_obj=driver, obj_in=driver_in)
        return driver
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="A driver with this email or license number already exists.",
        )

@router.delete("/driver/{driver_id}", response_model=schemas.UserInDB)
async def delete_driver(
    *,
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """
    Delete a driver.
    """
    driver = await crud.driver.get(db, id=driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver = await crud.driver.remove(db, id=driver_id)
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
