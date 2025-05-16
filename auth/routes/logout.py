from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from session import get_session
from db import queries
from db.models import User, Token
from utils import hash_pass, token_generate

api_router = APIRouter()

security = HTTPBearer()

@api_router.post(
    "/auth/logout",
    status_code=200,
)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    user_id = token_generate.verify_token(token)['id']
    return await queries.delete_token(session, user_id)
