from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """
    Dependency to get an async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Explicitly commit the transaction
        except Exception:
            await session.rollback() # Rollback on error
            raise
