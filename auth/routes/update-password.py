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

class UpdatePassword(BaseModel):
    current_password: str
    new_password: str

@api_router.post(
    "/auth/me",
    status_code=200,
)
async def update_password(
    passes: UpdatePassword,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    db_token = await queries.check_token(session, token)
    if not db_token or db_token.expires_at.timestamp() < datetime.utcnow().timestamp():
        raise HTTPException(status_code=401, detail="Incorrect token")
    
    payload = token_generate.verify_token(token)

    db_user = await queries.get_user(session, payload['id'])
    if db_user is None:
        raise HTTPException(status_code=401, detail="Username or password is incorrect")

    if not hash_pass.verify_password(passes.current_password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Username or password is incorrect")

    new_password_hash = hash_pass.get_password_hash(passes.new_password)
    db_user.password_hash = new_password_hash

    return await queries.update_user(session, db_user)
