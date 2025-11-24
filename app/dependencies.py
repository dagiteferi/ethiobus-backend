from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.crud.user import user as crud_user
from app.models.user import User, Passenger, Driver, Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")  # The token subject is the email
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user by email (the token subject is the email)
    user = await crud_user.get_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_passenger(current_user: User = Depends(get_current_user)) -> Passenger:
    if not isinstance(current_user, Passenger):
        raise HTTPException(status_code=403, detail="Not a passenger")
    return current_user

async def get_current_driver(current_user: User = Depends(get_current_user)) -> Driver:
    if not isinstance(current_user, Driver):
        raise HTTPException(status_code=403, detail="Not a driver")
    return current_user

async def get_current_admin(current_user: User = Depends(get_current_user)) -> Admin:
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=403, detail="Not an admin")
    return current_user
