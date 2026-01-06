from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from backend.config.settings import settings

DATABASE_URL = settings.DATABASE_URL

# Only create engine if DATABASE_URL is configured
if DATABASE_URL:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
    )
    
    SessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
else:
    engine = None
    SessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency for FastAPI"""
    if SessionLocal is None:
        raise RuntimeError("Database is not configured")
    async with SessionLocal() as session:
        yield session
