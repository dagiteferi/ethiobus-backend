import sys
import os
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import AsyncSessionLocal
from app.models.user import User, Admin, Driver, Passenger
from app.models.bus import Bus
from app.models.route import Route
from app.models.trip import Trip
from app.core.security import get_password_hash

async def seed_test_data():
    """
    Seeds the database with comprehensive test data for development.
    """
    db: AsyncSession = AsyncSessionLocal()
    try:
        print("Starting database seeding...")
        
        # Create Test Users
        print("Creating users...")
        
        # Admin user
        admin = Admin(
            email="admin@ethiobus.com",
            full_name="Admin User",
            phone="0911111111",
            password_hash=get_password_hash("admin123"),
        )
        db.add(admin)
        await db.flush()
        
        # Driver users
        driver1 = Driver(
            email="driver1@ethiobus.com",
            full_name="Abebe Bikila",
            phone="0922222222",
            password_hash=get_password_hash("driver123"),
            license_number="DRV001",
        )
        driver2 = Driver(
            email="driver2@ethiobus.com",
            full_name="Fatuma Roba",
            phone="0933333333",
            password_hash=get_password_hash("driver123"),
            license_number="DRV002",
        )
        driver3 = Driver(
            email="driver3@ethiobus.com",
            full_name="Tadesse Alemayehu",
            phone="0944444444",
            password_hash=get_password_hash("driver123"),
            license_number="DRV003",
        )
        db.add_all([driver1, driver2, driver3])
        await db.flush()
        
        # Passenger users
        passenger1 = Passenger(
            email="passenger1@test.com",
            full_name="Haile Gebrselassie",
            phone="0955555555",
            password_hash=get_password_hash("pass123"),
        )
        passenger2 = Passenger(
            email="passenger2@test.com",
            full_name="Tirunesh Dibaba",
            phone="0966666666",
            password_hash=get_password_hash("pass123"),
        )
        db.add_all([passenger1, passenger2])
        await db.commit()
        print("✓ Users created")
        
        # Create Buses
        print("Creating buses...")
        bus1 = Bus(
            plate_number="AA-1234-ET",
            model="Higer Luxury",
            total_seats=45,
            status="active",
        )
        bus2 = Bus(
            plate_number="AA-5678-ET",
            model="Yutong Premium",
            total_seats=49,
            status="active",
        )
        bus3 = Bus(
            plate_number="OR-9012-ET",
            model="Golden Dragon Standard",
            total_seats=35,
            status="active",
        )
        bus4 = Bus(
            plate_number="AM-3456-ET",
            model="Scania Comfort",
            total_seats=40,
            status="active",
        )
        db.add_all([bus1, bus2, bus3, bus4])
        await db.commit()
        
        # Assign buses to drivers
        driver1.assigned_bus_id = bus1.id
        driver2.assigned_bus_id = bus2.id
        driver3.assigned_bus_id = bus3.id
        db.add_all([driver1, driver2, driver3])
        await db.commit()
        print("✓ Buses created and assigned")
        
        # Create Routes (both directions for popular routes)
        print("Creating routes...")
        routes_data = [
            # Addis Ababa routes
            {"origin": "Addis Ababa", "destination": "Adama", "distance": 100, "duration": 120},
            {"origin": "Adama", "destination": "Addis Ababa", "distance": 100, "duration": 120},
            {"origin": "Addis Ababa", "destination": "Bahir Dar", "distance": 560, "duration": 420},
            {"origin": "Bahir Dar", "destination": "Addis Ababa", "distance": 560, "duration": 420},
            {"origin": "Addis Ababa", "destination": "Hawassa", "distance": 275, "duration": 240},
            {"origin": "Hawassa", "destination": "Addis Ababa", "distance": 275, "duration": 240},
            {"origin": "Addis Ababa", "destination": "Dire Dawa", "distance": 515, "duration": 360},
            {"origin": "Dire Dawa", "destination": "Addis Ababa", "distance": 515, "duration": 360},
            {"origin": "Addis Ababa", "destination": "Gondar", "distance": 740, "duration": 480},
            {"origin": "Gondar", "destination": "Addis Ababa", "distance": 740, "duration": 480},
            {"origin": "Addis Ababa", "destination": "Mekelle", "distance": 780, "duration": 540},
            {"origin": "Mekelle", "destination": "Addis Ababa", "distance": 780, "duration": 540},
        ]
        
        routes = []
        for route_data in routes_data:
            route = Route(
                origin=route_data["origin"],
                destination=route_data["destination"],
                distance_km=route_data["distance"],
                avg_duration_min=route_data["duration"],
            )
            routes.append(route)
        
        db.add_all(routes)
        await db.commit()
        await db.refresh(routes[0])  # Refresh to get IDs
        print(f"✓ {len(routes)} routes created")
        
        # Create a route lookup dictionary
        route_map = {}
        for route in routes:
            key = f"{route.origin}->{route.destination}"
            route_map[key] = route
        
        # Create Trips for the next 7 days
        print("Creating trips...")
        now = datetime.utcnow()
        trips = []
        
        # Addis Ababa -> Adama trips (multiple per day)
        addis_adama_route = route_map.get("Addis Ababa->Adama")
        if addis_adama_route:
            for day in range(7):
                for hour in [6, 8, 10, 12, 14, 16, 18]:
                    departure = now + timedelta(days=day, hours=hour)
                    arrival = departure + timedelta(minutes=120)
                    trip = Trip(
                        bus_id=bus1.id if hour % 2 == 0 else bus2.id,
                        route_id=addis_adama_route.id,
                        driver_id=driver1.id if hour % 2 == 0 else driver2.id,
                        departure_time=departure,
                        arrival_time=arrival,
                        base_price_etb=150.0 + (hour * 10),  # Varying prices
                        available_seats=bus1.total_seats if hour % 2 == 0 else bus2.total_seats,
                    )
                    trips.append(trip)
        
        # Adama -> Addis Ababa trips
        adama_addis_route = route_map.get("Adama->Addis Ababa")
        if adama_addis_route:
            for day in range(7):
                for hour in [7, 9, 11, 13, 15, 17, 19]:
                    departure = now + timedelta(days=day, hours=hour)
                    arrival = departure + timedelta(minutes=120)
                    trip = Trip(
                        bus_id=bus2.id if hour % 2 == 0 else bus3.id,
                        route_id=adama_addis_route.id,
                        driver_id=driver2.id if hour % 2 == 0 else driver3.id,
                        departure_time=departure,
                        arrival_time=arrival,
                        base_price_etb=150.0 + (hour * 10),
                        available_seats=bus2.total_seats if hour % 2 == 0 else bus3.total_seats,
                    )
                    trips.append(trip)
        
        # Addis Ababa -> Bahir Dar trips
        addis_bahir_route = route_map.get("Addis Ababa->Bahir Dar")
        if addis_bahir_route:
            for day in range(7):
                for hour in [6, 8, 14]:
                    departure = now + timedelta(days=day, hours=hour)
                    arrival = departure + timedelta(minutes=420)
                    trip = Trip(
                        bus_id=bus1.id,
                        route_id=addis_bahir_route.id,
                        driver_id=driver1.id,
                        departure_time=departure,
                        arrival_time=arrival,
                        base_price_etb=850.0,
                        available_seats=bus1.total_seats,
                    )
                    trips.append(trip)
        
        # Addis Ababa -> Hawassa trips
        addis_hawassa_route = route_map.get("Addis Ababa->Hawassa")
        if addis_hawassa_route:
            for day in range(7):
                for hour in [7, 9, 15]:
                    departure = now + timedelta(days=day, hours=hour)
                    arrival = departure + timedelta(minutes=240)
                    trip = Trip(
                        bus_id=bus2.id,
                        route_id=addis_hawassa_route.id,
                        driver_id=driver2.id,
                        departure_time=departure,
                        arrival_time=arrival,
                        base_price_etb=600.0,
                        available_seats=bus2.total_seats,
                    )
                    trips.append(trip)
        
        db.add_all(trips)
        await db.commit()
        print(f"✓ {len(trips)} trips created")
        
        print("\n" + "="*50)
        print("Database seeded successfully!")
        print("="*50)
        print("\nTest Accounts:")
        print("  Admin: admin@ethiobus.com / admin123")
        print("  Driver: driver1@ethiobus.com / driver123")
        print("  Passenger: passenger1@test.com / pass123")
        print("\nRoutes created:")
        for route in routes[:6]:  # Show first 6
            print(f"  {route.origin} → {route.destination}")
        print(f"  ... and {len(routes) - 6} more routes")
        print(f"\nTotal trips: {len(trips)}")
        print("="*50)
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        await db.rollback()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed_test_data())

