from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from session import get_session
from db import queries
from db.models import User
from utils import hash_pass

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

api_router = APIRouter()

@api_router.post(
    "/auth/register",
    status_code=200,
)
async def register_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    db_user = await queries.get_user_by_name(session, user.username)
    if db_user is not None:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_db_user = User(
        username = user.username,
        password_hash = hash_pass.hash_password(user.password),
        role = user.role
    )

    return await queries.create_user(session, new_db_user)
