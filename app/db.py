import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Convert standard postgres:// URL to postgresql+asyncpg:// for async support
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI to get a database session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()