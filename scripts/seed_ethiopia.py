
import sys
import os
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine, AsyncSessionLocal
from app.models.base import Base

from app.models import User, Passenger, Driver, Admin, Route, Bus, Trip, Booking
from app.core.security import get_password_hash

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    db: AsyncSession = AsyncSessionLocal()

    # Create Users
    admin1 = Admin(
        username="admin1",
        full_name="Abebe Kebede",
        phone="0911123456",
        password_hash=get_password_hash("adminpass"),
    )
    driver1 = Driver(
        username="driver1",
        full_name="Tadesse Alemayehu",
        phone="0912345678",
        password_hash=get_password_hash("driverpass"),
        license_number="DRV12345",
    )
    passenger1 = Passenger(
        username="passenger1",
        full_name="Selamawit Kassahun",
        phone="0923456789",
        password_hash=get_password_hash("passpass"),
    )
    passenger2 = Passenger(
        username="passenger2",
        full_name="Lulit Mesfin",
        phone="0934567890",
        password_hash=get_password_hash("passpass2"),
    )
    db.add_all([admin1, driver1, passenger1, passenger2])
    await db.commit()

    # Create Buses
    bus1 = Bus(
        plate_number="BA-123-ET",
        model="Higer KLQ6119",
        total_seats=45,
        status="active",
    )
    bus2 = Bus(
        plate_number="BA-456-ET",
        model="Yutong ZK6122H9",
        total_seats=49,
        status="active",
    )
    db.add_all([bus1, bus2])
    await db.commit()
    
    # Assign bus to driver
    driver1.assigned_bus_id = bus1.id
    db.add(driver1)
    await db.commit()

    # Create Routes
    route1 = Route(
        origin="Adama",
        destination="Addis Ababa",
        distance_km=100,
        avg_duration_min=120,
    )
    route2 = Route(
        origin="Bahir Dar",
        destination="Gondar",
        distance_km=180,
        avg_duration_min=240,
    )
    route3 = Route(
        origin="Hawassa",
        destination="Mekelle",
        distance_km=1200,
        avg_duration_min=1440,
    )
    db.add_all([route1, route2, route3])
    await db.commit()

    # Create Trip
    trip1 = Trip(
        bus_id=bus1.id,
        route_id=route1.id,
        driver_id=driver1.id,
        departure_time=datetime(2025, 11, 12, 7, 0),
        arrival_time=datetime(2025, 11, 12, 9, 0),
        base_price_etb=150.00,
        available_seats=bus1.total_seats,
    )
    db.add(trip1)
    await db.commit()

    # Create Bookings
    booking1 = Booking(
        passenger_id=passenger1.id,
        trip_id=trip1.id,
        seat_number="A1",
        is_paid=True,
        is_boarded=True, # one boarded
        payment_ref="MOCK-XYZ789",
    )
    booking2 = Booking(
        passenger_id=passenger2.id,
        trip_id=trip1.id,
        seat_number="B5",
        is_paid=True,
        is_boarded=False,
        payment_ref="MOCK-ABC123",
    )
    db.add_all([booking1, booking2])
    trip1.available_seats -= 2
    await db.commit()

    await db.close()
    print("Database has been seeded with initial data.")

if __name__ == "__main__":
    asyncio.run(seed_data())
