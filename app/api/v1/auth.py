from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.schemas.user import UserCreate

router = APIRouter()

@router.post("/register", response_model=schemas.UserInDB)
async def register(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
):
    """
    Register a new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user_by_phone = await crud.user.get_by_phone(db, phone=user_in.phone)
    if user_by_phone:
        raise HTTPException(
            status_code=400,
            detail="A user with this phone number already exists in the system.",
        )

    user = await crud.user.create(db, obj_in=user_in)
    return user

@router.post("/login", response_model=schemas.Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await crud.user.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
