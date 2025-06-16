from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from enum import Enum

class CallStatus(str, Enum):
    BOOKED = "BOOKED"
    NO_DEAL = "NO DEAL"
    NOT_ELIGIBLE = "NOT ELIGIBLE"

class Load(SQLModel, table=True):
    """Model for load data."""
    __tablename__ = "loads"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    origin_city: str
    origin_state: str
    dest_city: str
    dest_state: str
    equipment: str
    pickup_ts: datetime
    distance_mi: float
    offer_rate: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Call(SQLModel, table=True):
    """Model for call data."""
    __tablename__ = "calls"
    
    id: int = Field(default=None, primary_key=True)
    mc_number: str
    load_id: UUID = Field(foreign_key="loads.id")
    status: str = Field(..., description="Status of the call: BOOKED, NO DEAL, NOT ELIGIBLE")
    negotiated_rate: Optional[float] = None
    sentiment: Optional[str] = None
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic models for API requests/responses
class LoadSearch(SQLModel):
    """Schema for load search request."""
    origin: str
    dest: str
    equipment: str

class LoadResponse(SQLModel):
    id: UUID
    origin_city: str
    origin_state: str
    dest_city: str
    dest_state: str
    equipment: str
    pickup_ts: datetime
    distance_mi: float
    offer_rate: float
    rpm: float

class CallCreate(SQLModel):
    mc_number: str
    load_id: UUID
    status: CallStatus
    negotiated_rate: Optional[float] = None
    sentiment: Optional[str] = None

class CallLog(SQLModel):
    """Schema for call logging request."""
    mc_number: str
    load_id: UUID
    status: str
    negotiated_rate: Optional[float] = None
    sentiment: Optional[str] = None

class BestLoad(SQLModel, table=True):   # note: table=True maps to an existing view
    __tablename__ = "best_load"

    id           : str = Field(primary_key=True)
    origin_city  : str
    dest_city    : str
    equipment    : str
    pickup_ts    : str
    distance_mi  : float
    offer_rate   : float
    rpm          : float
    rank         : int