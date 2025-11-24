from .user import UserCreate, UserInDB, Token, TokenData, PassengerCreate, DriverCreate, AdminCreate, TokenWithUser, DriverWithBusCreate, DriverUpdate
from .trip import TripCreate, TripInDB
from .booking import BookingCreate, BookingInDB, BookingWithQR
from .report import RevenueReport, OccupancyReport, TopRoutesReport
from .bus import BusCreate, BusInDB, BusUpdate
from .route import RouteCreate, RouteInDB, RouteUpdate
from .driver import DriverRouteAssignment # Assuming this is where DriverRouteAssignment is defined

__all__ = [
    "UserCreate",
    "UserInDB",
    "Token",
    "TokenData",
    "PassengerCreate",
    "DriverCreate",
    "AdminCreate",
    "TokenWithUser",
    "DriverWithBusCreate", # Added
    "DriverUpdate", # Added
    "TripCreate",
    "TripInDB",
    "BookingCreate",
    "BookingInDB",
    "BookingWithQR",
    "RevenueReport",
    "OccupancyReport",
    "TopRoutesReport",
    "BusCreate",
    "BusInDB",
    "BusUpdate", # Added
    "RouteCreate",
    "RouteInDB",
    "RouteUpdate", # Added
    "DriverRouteAssignment", # Added
]
