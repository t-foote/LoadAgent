from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from .models import Call, LoadResponse


async def get_best_load(session: AsyncSession, origin: str, dest: str, equipment: str):
    query = text("""
        SELECT * FROM best_load 
        WHERE origin_city = :o AND dest_city = :d AND equipment = :e
        ORDER BY rpm DESC LIMIT 1
    """)
    result = await session.execute(query, {"o": origin, "d": dest, "e": equipment})
    row = result.fetchone()
    if row:
        # Convert row to LoadResponse
        return LoadResponse(
            id=row.id,
            origin_city=row.origin_city,
            origin_state=row.origin_state,
            dest_city=row.dest_city,
            dest_state=row.dest_state,
            equipment=row.equipment,
            pickup_ts=row.pickup_ts,
            distance_mi=row.distance_mi,
            offer_rate=row.offer_rate,
            rpm=row.rpm
        )
    return None


async def log_call(session: AsyncSession, call_data: Call):
    session.add(call_data)
    await session.commit()
    await session.refresh(call_data)
    return call_data
