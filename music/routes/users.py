from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from session import get_session
from clients import auth
from db.models import User, Artist
from db import queries

api_router = APIRouter()
security = HTTPBearer()

class CreateUser(BaseModel):
    username : str
    password: str
    role: str
    avatar_url : str | None

@api_router.post("/users/register")
async def create_user(
    user: CreateUser,
    session: AsyncSession = Depends(get_session),
):
    prev_db_user = await queries.get_user_by_name(session, user.username)
    if prev_db_user is not None:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    prev_db_artist = await queries.get_artist_by_name(session, user.username)
    if prev_db_artist is not None:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = {
        "username": user.username,
        "password": user.password,
        "role": user.role
    }
    client = auth.AuthClient()
    auth_response = await client.register(new_user)
    ext_id = auth_response["id"]
    if user.role == "user":
        db_user = User(
            external_id = ext_id,
            username = user.username,
            avatar_url = user.avatar_url
        )
        return await queries.create_user(session, db_user)
    
    elif user.role == "artist":
        db_artist = Artist(
            external_id = ext_id,
            username = user.username,
            avatar_url = user.avatar_url
        )
        return await queries.create_user(session, db_artist)


@api_router.get("/users/me")
async def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")
    
    username = auth_response["username"]
    role = auth_response["role"] 
    get_user = {
        "username": username,
        "role": role,
        "external_id": auth_response["id"]
    }

    if role == "user":
        db_user = await queries.get_user_by_name(session, username)
    elif role == "artist":
        db_user = await queries.get_artist_by_name(session, username)

    get_user["avatar_url"] = db_user.avatar_url
    get_user["id"] = db_user.id

    return get_user


class PatchUser(BaseModel):
    username : str | None
    avatar_url : str | None

@api_router.put("/users/me")
async def patch_user(
    new_data: PatchUser,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    username = auth_response["username"]
    role = auth_response["role"]

    if role == "user":
        db_user = await queries.get_user_by_name(session, username)

        if new_data.username:
            await queries.update_user_username(session, db_user.id, new_data.username)
        if new_data.avatar_url:
            await queries.update_user_avatar(session, db_user.id, new_data.avatar_url)

    elif role == "artist":
        db_user = await queries.get_artist_by_name(session, username)

        if new_data.username:
            await queries.update_artist_username(session, db_user.id, new_data.username)
        if new_data.avatar_url:
            await queries.update_artist_avatar(session, db_user.id, new_data.avatar_url)

    return {
        "status": "OK"
    }
