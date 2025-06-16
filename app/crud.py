from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from .models import Call, LoadResponse, Load, CallLog, LoadSearch
from app.models import BestLoad

async def get_best_load(session, search):
    """Get the best load matching the search criteria."""
    stmt = (
        select(BestLoad)
        .where(
            BestLoad.origin_city == search.origin,
            BestLoad.dest_city   == search.dest,
            BestLoad.equipment   == search.equipment,
            BestLoad.rank        == 1,
        )
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


# async def get_best_load(session: AsyncSession, search: LoadSearch) -> Load:
#     """Get the best load matching the search criteria."""
#     query = select(Load).where(
#         Load.origin_city == search.origin,
#         Load.dest_city == search.dest,
#         Load.equipment == search.equipment
#     ).order_by(Load.rpm.desc()).limit(1)
    
#     result = await session.execute(query)
#     return result.scalar_one_or_none()


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
