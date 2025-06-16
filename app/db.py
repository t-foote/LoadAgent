import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url
from sqlalchemy import text
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
    """Initialize tables _and_ your custom view."""
    async with engine.begin() as conn:
        # 1) Create all SQLModel tables
        await conn.run_sync(SQLModel.metadata.create_all)
        # 2) Load and execute your full schema including views
        schema_file = Path(__file__).parent.parent / "db" / "schema.sql"
        ddl = schema_file.read_text()
        await conn.execute(text(ddl))

async def get_session() -> AsyncSession:
    """Get a database session."""
    async with async_session() as session:
        yield session