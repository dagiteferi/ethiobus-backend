
import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import AsyncSessionLocal as SessionLocal
from app.models.user import Admin, Driver, Passenger
from app.models.bus import Bus
from app.models.route import Route
from app.models.trip import Trip
from app.core.security import get_password_hash
from app import crud, schemas
from datetime import datetime, timedelta

async def seed_data():
    """
    Seeds the database with initial data.
    """
    db: AsyncSession = SessionLocal()
    try:
        # Create default admin user if not exists
        default_admin_email = "admin@gmail.com"
        existing_admin = await crud.user.get_by_email(db, email=default_admin_email)
        if not existing_admin:
            print(f"Creating default admin user: {default_admin_email}")
            admin_in = schemas.user.AdminCreate(
                email=default_admin_email,
                full_name="Default Admin",
                phone="0900000000", # Placeholder phone number
                username="default_admin",
                password="admin@1234",
                role="admin"
            )
            await crud.user.create(db, obj_in=admin_in)
            await db.commit()
        else:
            print(f"Default admin user '{default_admin_email}' already exists.")

        # Create Admins
        # Create Admins
        # Using crud.user.create for better handling of unique constraints
        admin_seed_data = [
            {
                "username": "admin1_seed",
                "email": "admin1@example.com",
                "full_name": "Admin User 1",
                "phone": "0911111112",
                "password": "adminpass1",
                "role": "admin"
            },
            {
                "username": "admin2_seed",
                "email": "admin2@example.com",
                "full_name": "Admin User 2",
                "phone": "0922222223",
                "password": "adminpass2",
                "role": "admin"
            }
        ]

        created_admins = [] # New list to store admin objects
        for admin_data in admin_seed_data:
            admin_obj = None
            try:
                print(f"Attempting to create admin user: {admin_data['email']}")
                admin_in = schemas.user.AdminCreate(**admin_data)
                admin_obj = await crud.user.create(db, obj_in=admin_in)
                print(f"Successfully created admin user: {admin_data['email']}")
            except ValueError as e:
                print(f"Skipping admin user '{admin_data['email']}' creation: {e}")
                # If user already exists, retrieve it using any unique identifier
                admin_obj = await crud.user.get_by_email(db, email=admin_data["email"])
                if not admin_obj and admin_data.get("phone"):
                    admin_obj = await crud.user.get_by_phone(db, phone=admin_data["phone"])
                if not admin_obj and admin_data.get("username"):
                    admin_obj = await crud.user.get_by_username(db, username=admin_data["username"])
            
            if admin_obj: # Ensure admin_obj is not None before appending
                created_admins.append(admin_obj)
        await db.commit() # Commit after all admin creations

        # Create Buses
        bus_seed_data = [
            {"plate_number": "AA-A1234", "model": "Toyota Coaster", "total_seats": 28},
            {"plate_number": "OR-B5678", "model": "Fuso Canter", "total_seats": 32},
            {"plate_number": "AM-C9101", "model": "Golden Dragon", "total_seats": 45},
        ]

        created_buses = []
        for bus_data in bus_seed_data:
            existing_bus = await crud.bus.get_by_plate_number(db, plate_number=bus_data["plate_number"])
            if not existing_bus:
                print(f"Creating bus with plate number: {bus_data['plate_number']}")
                bus_in = schemas.bus.BusCreate(**bus_data)
                new_bus = await crud.bus.create(db, obj_in=bus_in)
                created_buses.append(new_bus)
            else:
                print(f"Bus with plate number '{bus_data['plate_number']}' already exists.")
                created_buses.append(existing_bus)
        await db.commit()

        # Assign created/existing buses to variables for later use
        bus1 = created_buses[0]
        bus2 = created_buses[1]
        bus3 = created_buses[2]

        # Create Drivers
        driver_seed_data = [
            {
                "username": "driver1",
                "email": "driver1@example.com",
                "full_name": "Abebe Bikila",
                "phone": "0933333333",
                "password": "driverpass1",
                "license_number": "DRV12345",
                "assigned_bus_id": bus1.id,
                "role": "driver"
            },
            {
                "username": "driver2",
                "email": "driver2@example.com",
                "full_name": "Fatuma Roba",
                "phone": "0944444444",
                "password": "driverpass2",
                "license_number": "DRV54321",
                "assigned_bus_id": bus2.id,
                "role": "driver"
            }
        ]

        created_drivers = []
        for driver_data in driver_seed_data:
            driver_obj = None
            try:
                print(f"Attempting to create driver user: {driver_data['email']}")
                driver_in = schemas.user.DriverCreate(**driver_data)
                driver_obj = await crud.user.create(db, obj_in=driver_in)
                print(f"Successfully created driver user: {driver_data['email']}")
            except ValueError as e:
                print(f"Skipping driver user '{driver_data['email']}' creation: {e}")
                # If user already exists, retrieve it using any unique identifier
                driver_obj = await crud.user.get_by_email(db, email=driver_data["email"])
                if not driver_obj and driver_data.get("phone"):
                    driver_obj = await crud.user.get_by_phone(db, phone=driver_data["phone"])
                if not driver_obj and driver_data.get("username"):
                    driver_obj = await crud.user.get_by_username(db, username=driver_data["username"])
            
            if driver_obj: # Ensure driver_obj is not None before appending
                created_drivers.append(driver_obj)
        await db.commit() # Commit after all driver creations

        # Assign created/existing drivers to variables for later use
        driver1 = created_drivers[0]
        driver2 = created_drivers[1]

        # Create Passengers
        passenger_seed_data = [
            {
                "username": "passenger1",
                "email": "passenger1@example.com", # Added email
                "full_name": "Haile Gebrselassie",
                "phone": "0955555555",
                "password": "pass1",
                "role": "passenger"
            },
            {
                "username": "passenger2",
                "email": "passenger2@example.com", # Added email
                "full_name": "Tirunesh Dibaba",
                "phone": "0966666666",
                "password": "pass2",
                "role": "passenger"
            }
        ]

        created_passengers = [] # New list to store passenger objects
        for passenger_data in passenger_seed_data:
            passenger_obj = None
            try:
                print(f"Attempting to create passenger user: {passenger_data['email']}")
                passenger_in = schemas.user.PassengerCreate(**passenger_data)
                passenger_obj = await crud.user.create(db, obj_in=passenger_in)
                print(f"Successfully created passenger user: {passenger_data['email']}")
            except ValueError as e:
                print(f"Skipping passenger user '{passenger_data['email']}' creation: {e}")
                # If user already exists, retrieve it using any unique identifier
                passenger_obj = await crud.user.get_by_email(db, email=passenger_data["email"])
                if not passenger_obj and passenger_data.get("phone"):
                    passenger_obj = await crud.user.get_by_phone(db, phone=passenger_data["phone"])
                if not passenger_obj and passenger_data.get("username"):
                    passenger_obj = await crud.user.get_by_username(db, username=passenger_data["username"])
            
            if passenger_obj: # Ensure passenger_obj is not None before appending
                created_passengers.append(passenger_obj)
        await db.commit() # Commit after all passenger creations

        # Create Routes
        route_seed_data = [
            {"origin": "Addis Ababa", "destination": "Bahir Dar", "distance_km": 560, "avg_duration_min": 7 * 60},
            {"origin": "Addis Ababa", "destination": "Hawassa", "distance_km": 275, "avg_duration_min": 4 * 60},
            {"origin": "Gondar", "destination": "Axum", "distance_km": 180, "avg_duration_min": 3 * 60},
        ]

        created_routes = []
        for route_data in route_seed_data:
            existing_route = await crud.route.get_by_source_and_destination(
                db, source=route_data["origin"], destination=route_data["destination"]
            )
            if not existing_route:
                print(f"Creating route from {route_data['origin']} to {route_data['destination']}")
                route_in = schemas.route.RouteCreate(**route_data)
                new_route = await crud.route.create(db, obj_in=route_in)
                created_routes.append(new_route)
            else:
                print(f"Route from {route_data['origin']} to {route_data['destination']} already exists.")
                created_routes.append(existing_route)
        await db.commit()

        # Assign created/existing routes to variables for later use
        route1 = created_routes[0]
        route2 = created_routes[1]
        route3 = created_routes[2]

        # Create Trips
        now = datetime.utcnow()
        # Create trips for today for easier testing
        trip_seed_data = [
            {
                "bus_id": bus1.id,
                "route_id": route1.id,
                "driver_id": driver1.id,
                "departure_time": now + timedelta(hours=2), # For today
                "arrival_time": now + timedelta(hours=9),   # For today
                "base_price_etb": 800.00,
                "available_seats": bus1.total_seats,
            },
            {
                "bus_id": bus2.id,
                "route_id": route2.id,
                "driver_id": driver2.id,
                "departure_time": now + timedelta(hours=4), # For today
                "arrival_time": now + timedelta(hours=8),   # For today
                "base_price_etb": 450.00,
                "available_seats": bus2.total_seats,
            },
        ]

        for trip_data in trip_seed_data:
            existing_trip = await crud.trip.get_by_details(
                db,
                bus_id=trip_data["bus_id"],
                route_id=trip_data["route_id"],
                departure_time=trip_data["departure_time"],
            )
            if not existing_trip:
                print(f"Creating trip for bus {trip_data['bus_id']} on route {trip_data['route_id']}")
                trip_in = schemas.trip.TripCreate(**trip_data)
                await crud.trip.create(db, obj_in=trip_in)
            else:
                print(f"Trip for bus {trip_data['bus_id']} on route {trip_data['route_id']} at {trip_data['departure_time']} already exists.")
        await db.commit()

        print("Database seeded successfully!")

    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
