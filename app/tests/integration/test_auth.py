import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
from app.core.config import settings

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(name="test_db")
async def test_db_fixture():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        await db.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(name="client")
async def client_fixture(test_db: AsyncSession):
    app.dependency_overrides[get_db] = lambda: test_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_register_and_login_user(client: AsyncClient):
    # Test registration
    register_data = {
        "email": "testuser@example.com",
        "full_name": "Test User",
        "phone": "0912345678",
        "password": "testpassword",
        "role": "passenger"
    }
    response = await client.post("/api/v1/register", json=register_data)
    assert response.status_code == 200
    registered_user = response.json()
    assert registered_user["email"] == "testuser@example.com"
    assert "id" in registered_user
    assert "password_hash" not in registered_user # Ensure password hash is not returned

    # Test login
    login_data = {
        "username": "testuser@example.com",
        "password": "testpassword"
    }
    response = await client.post("/api/v1/login", data=login_data)
    assert response.status_code == 200
    login_response = response.json()
    assert "access_token" in login_response
    assert login_response["token_type"] == "bearer"
    assert login_response["user"]["email"] == "testuser@example.com"
    assert login_response["user"]["full_name"] == "Test User"

    # Test login with incorrect password
    login_data_incorrect = {
        "username": "testuser@example.com",
        "password": "wrongpassword"
    }
    response = await client.post("/api/v1/login", data=login_data_incorrect)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

    # Test registration with existing email
    response = await client.post("/api/v1/register", json=register_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "The user with this email already exists in the system."

    # Test registration with existing phone
    register_data_existing_phone = {
        "email": "anotheruser@example.com",
        "full_name": "Another User",
        "phone": "0912345678", # Same phone as registered user
        "password": "anotherpassword",
        "role": "passenger"
    }
    response = await client.post("/api/v1/register", json=register_data_existing_phone)
    assert response.status_code == 400
    assert response.json()["detail"] == "A user with this phone number already exists in the system."
