
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
        admin1 = Admin(
            username="admin1_seed", # Changed username
            email="admin1@example.com",
            full_name="Admin User 1",
            phone="0911111112",
            password_hash=get_password_hash("adminpass1"),
        )
        admin2 = Admin(
            username="admin2_seed", # Changed username
            email="admin2@example.com",
            full_name="Admin User 2",
            phone="0922222223",
            password_hash=get_password_hash("adminpass2"),
        )
        db.add_all([admin1, admin2])
        await db.commit()

        # Create Buses
        bus1 = Bus(plate_number="AA-A1234", model="Toyota Coaster", total_seats=28)
        bus2 = Bus(plate_number="OR-B5678", model="Fuso Canter", total_seats=32)
        bus3 = Bus(plate_number="AM-C9101", model="Golden Dragon", total_seats=45)
        db.add_all([bus1, bus2, bus3])
        await db.commit()

        # Create Drivers
        driver1 = Driver(
            username="driver1",
            email="driver1@example.com", # Added email
            full_name="Abebe Bikila",
            phone="0933333333",
            password_hash=get_password_hash("driverpass1"),
            license_number="DRV12345",
            assigned_bus_id=bus1.id,
        )
        driver2 = Driver(
            username="driver2",
            email="driver2@example.com", # Added email
            full_name="Fatuma Roba",
            phone="0944444444",
            password_hash=get_password_hash("driverpass2"),
            license_number="DRV54321",
            assigned_bus_id=bus2.id,
        )
        db.add_all([driver1, driver2])
        await db.commit()

        # Create Passengers
        passenger1 = Passenger(
            username="passenger1",
            full_name="Haile Gebrselassie",
            phone="0955555555",
            password_hash=get_password_hash("pass1"),
        )
        passenger2 = Passenger(
            username="passenger2",
            full_name="Tirunesh Dibaba",
            phone="0966666666",
            password_hash=get_password_hash("pass2"),
        )
        db.add_all([passenger1, passenger2])
        await db.commit()

        # Create Routes
        route1 = Route(
            origin="Addis Ababa",
            destination="Bahir Dar",
            distance_km=560,
            avg_duration_min=7 * 60,
        )
        route2 = Route(
            origin="Addis Ababa",
            destination="Hawassa",
            distance_km=275,
            avg_duration_min=4 * 60,
        )
        route3 = Route(
            origin="Gondar",
            destination="Axum",
            distance_km=180,
            avg_duration_min=3 * 60,
        )
        db.add_all([route1, route2, route3])
        await db.commit()

        # Create Trips
        now = datetime.utcnow()
        trip1 = Trip(
            bus_id=bus1.id,
            route_id=route1.id,
            driver_id=driver1.id,
            departure_time=now + timedelta(days=1, hours=2),
            arrival_time=now + timedelta(days=1, hours=9),
            base_price_etb=800.00,
            available_seats=bus1.total_seats,
        )
        trip2 = Trip(
            bus_id=bus2.id,
            route_id=route2.id,
            driver_id=driver2.id,
            departure_time=now + timedelta(days=1, hours=4),
            arrival_time=now + timedelta(days=1, hours=8),
            base_price_etb=450.00,
            available_seats=bus2.total_seats,
        )
        db.add_all([trip1, trip2])
        await db.commit()

        print("Database seeded successfully!")

    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
