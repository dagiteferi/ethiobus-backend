
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

async def create_golden_path_data(db: AsyncSession):
    """
    Creates a specific, predictable scenario for end-to-end testing.
    """
    print("\n--- Creating Golden Path Data for Testing ---")

    # 1. Create Test Driver
    test_driver_email = "driver.test@ethiobus.com"
    existing_driver = await crud.user.get_by_email(db, email=test_driver_email)
    if not existing_driver:
        driver_in = schemas.DriverCreate(
            email=test_driver_email,
            password="password123",
            full_name="Test Driver",
            phone="0911223344",
            license_number="GOLDEN123",
            assigned_bus_id=None,
            role="driver",
            username="testdriver"
        )
        test_driver = await crud.driver.create(db, obj_in=driver_in)
        print(f"Created Test Driver: {test_driver.email}")
    else:
        test_driver = existing_driver
        print("Test Driver already exists.")

    # 2. Create Test Passenger
    test_passenger_email = "passenger.test@ethiobus.com"
    existing_passenger = await crud.user.get_by_email(db, email=test_passenger_email)
    if not existing_passenger:
        passenger_in = schemas.PassengerCreate(
            email=test_passenger_email,
            password="password123",
            full_name="Test Passenger",
            phone="0955667788",
            role="passenger",
            username="testpassenger"
        )
        test_passenger = await crud.user.create(db, obj_in=passenger_in)
        print(f"Created Test Passenger: {test_passenger.email}")
    else:
        test_passenger = existing_passenger
        print("Test Passenger already exists.")

    # 3. Create a specific Bus for the trip
    test_bus_plate = "AA-GOLD-01"
    existing_bus = await crud.bus.get_by_plate_number(db, plate_number=test_bus_plate)
    if not existing_bus:
        bus_in = schemas.BusCreate(
            plate_number=test_bus_plate,
            model="Golden Path Bus",
            total_seats=50
        )
        test_bus = await crud.bus.create(db, obj_in=bus_in)
        print(f"Created Test Bus: {test_bus.plate_number}")
    else:
        test_bus = existing_bus
        print("Test Bus already exists.")

    # 4. Create a specific Route
    test_route_origin = "Addis Ababa"
    test_route_destination = "Adama"
    existing_route = await crud.route.get_by_source_and_destination(db, source=test_route_origin, destination=test_route_destination)
    if not existing_route:
        route_in = schemas.RouteCreate(
            origin=test_route_origin,
            destination=test_route_destination,
            distance_km=100,
            avg_duration_min=120
        )
        test_route = await crud.route.create(db, obj_in=route_in)
        print(f"Created Test Route: {test_route.origin} to {test_route.destination}")
    else:
        test_route = existing_route
        print("Test Route already exists.")

    # 5. Create a specific Trip for today
    test_trip_departure = datetime.utcnow() + timedelta(hours=3)
    existing_trip = await crud.trip.get_by_details(db, bus_id=test_bus.id, route_id=test_route.id, departure_time=test_trip_departure)
    if not existing_trip:
        trip_in = schemas.TripCreate(
            bus_id=test_bus.id,
            route_id=test_route.id,
            driver_id=test_driver.id,
            departure_time=test_trip_departure,
            arrival_time=test_trip_departure + timedelta(minutes=120),
            base_price_etb=250.00,
            available_seats=test_bus.total_seats,
        )
        test_trip = await crud.trip.create(db, obj_in=trip_in)
        print(f"Created Test Trip for today from {test_route.origin} to {test_route.destination}")
    else:
        test_trip = existing_trip
        print("Test Trip already exists.")

    # 6. Create a booking for the test passenger on the test trip
    # This part is tricky because create_with_seat_check does not commit.
    # We will create it directly for simplicity in seeding.
    try:
        booking = await crud.booking.create_with_seat_check(
            db,
            trip_id=test_trip.id,
            passenger_id=test_passenger.id,
            seat_number="A1"
        )
        print(f"Booked seat A1 for {test_passenger.email} on trip {test_trip.id}")
    except ValueError as e:
        print(f"Could not create booking: {e}")


    await db.commit()
    print("--- Golden Path Data Creation Complete ---")


async def main():
    await seed_ethiopia_data()
    db: AsyncSession = SessionLocal()
    try:
        await create_golden_path_data(db)
    finally:
        await db.close()

if __name__ == "__main__":
    print("Running the Ethiopia data seeder...")
    asyncio.run(main())
