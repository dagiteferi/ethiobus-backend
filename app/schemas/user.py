from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    email: str
    full_name: str
    phone: str = Field(..., pattern=r"^09\d{8}$")
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., max_length=72)
    role: str = "passenger"

class UserInDB(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class PassengerCreate(UserCreate):
    role: str = "passenger"

class DriverCreate(UserCreate):
    role:str = "driver"
    license_number: str
    assigned_bus_id: Optional[int] = None

class AdminCreate(UserCreate):
    role: str = "admin"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class DriverWithBusCreate(UserBase):
    password: str = Field(..., max_length=72)
    license_number: str
    # Bus details
    plate_number: str
    model: str
    total_seats: int
