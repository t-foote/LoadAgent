from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from .models import Call, LoadResponse, Load, CallLog, LoadSearch


async def get_best_load(session: AsyncSession, search: LoadSearch) -> Load:
    """Get the best load matching the search criteria."""
    query = text("""
        SELECT * FROM best_load 
        WHERE origin_city = :origin 
        AND dest_city = :dest 
        AND equipment = :equipment
        ORDER BY rpm DESC 
        LIMIT 1
    """)
    result = await session.execute(
        query,
        {
            "origin": search.origin,
            "dest": search.dest,
            "equipment": search.equipment
        }
    )
    return result.scalar_one_or_none()


async def log_call(session: AsyncSession, call: CallLog) -> Call:
    """Log a call in the database."""
    db_call = Call(
        mc_number=call.mc_number,
        load_id=call.load_id,
        status=call.status,
        negotiated_rate=call.negotiated_rate,
        sentiment=call.sentiment
    )
    session.add(db_call)
    await session.commit()
    await session.refresh(db_call)
    return db_call
