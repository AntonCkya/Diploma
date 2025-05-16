from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from session import get_session
from db import queries
from db.models import User, Token
from utils import hash_pass, token_generate
from datetime import datetime

api_router = APIRouter()

security = HTTPBearer()

@api_router.post(
    "/auth/me",
    status_code=200,
)
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    db_token = await queries.check_token(session, token)
    if not db_token or db_token.expires_at.timestamp() < datetime.utcnow().timestamp():
        raise HTTPException(status_code=401, detail="Incorrect token")
    
    payload = token_generate.verify_token(token)

    return {
        "id": payload['id'],
        "username": payload['username'],
        "role": payload['role'],
        "created_at": payload['created_at']
    }
