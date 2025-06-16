import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url
from sqlmodel import SQLModel

# Get database URL from environment variable
_raw_url = os.getenv("DATABASE_URL")
if not _raw_url:
    raise ValueError("DATABASE_URL environment variable is not set")

url = make_url(_raw_url)
if url.drivername == "postgresql":
    url = url.set(drivername="postgresql+asyncpg")

engine = create_async_engine(url.render_as_string(hide_password=False),
                             echo=True)


# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Initialize the database."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """Get a database session."""
    async with async_session() as session:
        yield session