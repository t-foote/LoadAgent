import os
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from .db import get_session
from .models import LoadSearch, LoadResponse, Call, CallCreate
from .crud import get_best_load, log_call

app = FastAPI(title="LoadAgent API")

# API Key authentication
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key"
    )

@app.post("/search_loads", response_model=Optional[LoadResponse])
async def search_loads(
    request: LoadSearch,
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(get_api_key)
):
    """Search for the best available load based on origin, destination and equipment type."""
    load = await get_best_load(session, request.origin, request.dest, request.equipment)
    if not load:
        return None
    return load

@app.post("/log_call", response_model=Call)
async def create_call_log(
    request: CallCreate,
    session: AsyncSession = Depends(get_session),
    api_key: str = Depends(get_api_key)
):
    """Log details of a call with a carrier including negotiation outcome."""
    call_data = Call.from_orm(request)
    result = await log_call(session, call_data)
    return result

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Render."""
    return {"status": "ok"}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-happyrobot-domain.com"],  # Update this with your actual HappyRobot domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=10000, reload=True)