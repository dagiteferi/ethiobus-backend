
import sys
import os
import asyncio
import random
from datetime import datetime, timedelta
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import crud, schemas
from app.core.database import AsyncSessionLocal as SessionLocal, engine
from app.models.base import Base
from app.core.security import get_password_hash
from app.models import User, Passenger, Driver, Admin, Route, Bus, Trip, Booking

# Sample data
ETHIOPIAN_NAMES = [
    "Abebe Bikila", "Kenenisa Bekele", "Haile Gebrselassie", "Tirunesh Dibaba",
    "Derartu Tulu", "Fatuma Roba", "Meseret Defar", "Almaz Ayana",
    "Girma Wolde-Giorgis", "Meles Zenawi", "Sahle-Work Zewde", "Abiy Ahmed",
    "Liya Kebede", "Marcus Samuelsson", "Tedros Adhanom", "Emahoy Tsegué-Maryam Guèbrou"
]

BUS_MODELS = [
    "Mercedes-Benz Tourismo", "Volvo 9700", "Scania Irizar i8", "MAN Lion's Coach",
    "Golden Dragon", "Yutong T12", "King Long", "Higer Luxury"
]

async def seed_ethiopia_data():
    """
    Seeds the database with a more diverse and realistic set of Ethiopian data.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    db: AsyncSession = SessionLocal()
    try:
        print("--- Starting Ethiopian Data Seeding ---")

        # --- 1. Create Buses ---
        buses = []
        for i in range(15):
            plate_number = f"ET-{random.randint(1000, 9999)}-{i:02d}"
            bus_in = schemas.BusCreate(
                plate_number=plate_number,
                model=random.choice(BUS_MODELS),
                total_seats=random.choice([45, 49, 53]),
            )
            # Check if bus exists before creating
            existing_bus = await crud.bus.get_by_plate_number(db, plate_number=plate_number)
            if not existing_bus:
                bus = await crud.bus.create(db, obj_in=bus_in)
                buses.append(bus)
                print(f"Created Bus: {bus.model} ({bus.plate_number})")
        if not buses:
             print("Buses already exist, skipping creation.")
        await db.commit()

        # --- 2. Create Drivers ---
        drivers = []
        for i, name in enumerate(ETHIOPIAN_NAMES[:15]):
            email = f"{name.lower().replace(' ', '.')}{i}@ethiobus.com"
            driver_in = schemas.DriverCreate(
                email=email,
                password="password123",
                full_name=name,
                phone=f"09{random.randint(10000000, 99999999)}",
                license_number=f"DL{random.randint(100000, 999999)}",
                assigned_bus_id=None, # Assign later or handle dynamically
                role="driver",
                username=f"{name.lower().replace(' ', '')}{i}"
            )
            # Check if driver exists
            existing_driver = await crud.user.get_by_email(db, email=email)
            if not existing_driver:
                driver = await crud.driver.create(db, obj_in=driver_in)
                drivers.append(driver)
                print(f"Created Driver: {driver.full_name}")
        if not drivers:
            print("Drivers already exist, skipping creation.")
        await db.commit()

        # --- 3. Create Routes ---
        cities = [
            "Addis Ababa", "Adama", "Bahir Dar", "Mekelle", "Hawassa",
            "Gondar", "Jijiga", "Dire Dawa", "Jimma", "Harar"
        ]
        routes = []
        for _ in range(20): # Create 20 random routes
            origin, destination = random.sample(cities, 2)
            distance = random.randint(100, 800)
            route_in = schemas.RouteCreate(
                origin=origin,
                destination=destination,
                distance_km=distance,
                avg_duration_min=int(distance * 1.5) # Approximate duration
            )
            # Check if route exists
            existing_route = await crud.route.get_by_source_and_destination(db, source=origin, destination=destination)
            if not existing_route:
                route = await crud.route.create(db, obj_in=route_in)
                routes.append(route)
                print(f"Created Route: {route.origin} to {route.destination}")
        if not routes:
            print("Routes already exist, skipping creation.")
        await db.commit()

        # --- 4. Create Trips ---
        # Fetch all routes, buses, drivers if they were not created in this run
        all_routes = await crud.route.get_multi(db, limit=100)
        all_buses = await crud.bus.get_multi(db, limit=100)
        all_drivers = await crud.driver.get_multi(db, limit=100)

        if not all_routes or not all_buses or not all_drivers:
            print("Cannot create trips: Missing routes, buses, or drivers.")
            return

        print(f"Found {len(all_routes)} routes, {len(all_buses)} buses, {len(all_drivers)} drivers.")

        for route in all_routes:
            # Create 1 to 5 trips for each route
            for i in range(random.randint(1, 5)):
                departure_time = datetime.utcnow() + timedelta(days=random.randint(0, 7), hours=random.randint(6, 22))
                
                # Ensure there's at least one bus and driver
                if not all_buses or not all_drivers:
                    continue

                bus = random.choice(all_buses)
                driver = random.choice(all_drivers)

                trip_in = schemas.TripCreate(
                    bus_id=bus.id,
                    route_id=route.id,
                    driver_id=driver.id,
                    departure_time=departure_time,
                    arrival_time=departure_time + timedelta(minutes=route.avg_duration_min),
                    base_price_etb=round(route.distance_km * 0.75, 2),
                    available_seats=bus.total_seats,
                )
                # Check if trip exists
                existing_trip = await crud.trip.get_by_details(db, bus_id=bus.id, route_id=route.id, departure_time=departure_time)
                if not existing_trip:
                    await crud.trip.create(db, obj_in=trip_in)
                    print(f"Created Trip: {route.origin} -> {route.destination} at {departure_time.strftime('%Y-%m-%d %H:%M')}")

        await db.commit()

        print("\n--- Ethiopian Data Seeding Completed Successfully! ---")

    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        await db.rollback()
    finally:
        await db.close()

if __name__ == "__main__":
    print("Running the Ethiopia data seeder...")
    asyncio.run(seed_ethiopia_data())
