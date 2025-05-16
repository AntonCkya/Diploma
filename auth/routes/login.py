from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from session import get_session
from db import queries
from db.models import User, Token
from utils import hash_pass, token_generate

class UserLogin(BaseModel):
    username: str
    password: str

api_router = APIRouter()

@api_router.post(
    "/auth/login",
    status_code=200,
)
async def login_user(
    user: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    db_user = await queries.get_user_by_name(session, user.username)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Username or password is incorrect")

    if not hash_pass.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Username or password is incorrect")

    token_payload = {
        'id': db_user.id,
        'username': db_user.username,
        'role': db_user.role,
        'created_at': str(db_user.created_at)
    }
    token, expire = token_generate.create_access_token(token_payload)
    db_token = Token(
        user_id = db_user.id,
        token = token,
        expires_at = expire
    )

    await queries.delete_token(session, db_user.id)
    await queries.save_token(session, db_token)

    return {
        'token': token
    }
