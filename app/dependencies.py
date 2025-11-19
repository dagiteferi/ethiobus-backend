from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.crud.user import user as crud_user
from app.models.user import User, Passenger, Driver, Admin
from app.schemas.user import TokenData

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
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await crud_user.get_by_username(db, username=token_data.username)
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
