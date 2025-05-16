from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from clients import sample, auth
from db.models import Subscribe
from db import queries

api_router = APIRouter()
security = HTTPBearer()


@api_router.post("/artists/{artist_id}/subscribe")
async def subscribe_artist(
    artist_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    if auth_response["role"] == "artist":
        raise HTTPException(status_code=403, detail="Artists cannot subscribe")

    db_user = await queries.get_user_by_name(session, auth_response["username"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_artist = await queries.get_artist(session, artist_id)
    if not db_artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    subscribe = Subscribe(user_id=db_user.id, artist_id=artist_id)
    return await queries.create_subscribe(session, subscribe)


@api_router.delete("/artists/{artist_id}/subscribe")
async def unsubscribe_artist(
    artist_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    if auth_response["role"] == "artist":
        raise HTTPException(status_code=403, detail="Artists cannot unsubscribe")

    db_user = await queries.get_user_by_name(session, auth_response["username"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    subscribe = Subscribe(user_id=db_user.id, artist_id=artist_id)
    await queries.delete_subscribe(session, subscribe)


@api_router.get("/users/me/subscriptions")
async def get_user_subscriptions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    if auth_response["role"] == "artist":
        raise HTTPException(status_code=403, detail="Artists cannot have subscriptions")

    db_user = await queries.get_user_by_name(session, auth_response["username"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    subscriptions = await queries.get_user_subscriptions(
        session,
        user_id=db_user.id,
        limit=limit,
        offset=offset
    )

    return [
        {
            "artist": {
                "id": artist.id,
                "username": artist.username,
                "avatar_url": artist.avatar_url
            },
            "subscribed_at": subscribe.created_at.isoformat()
        }
        for subscribe, artist in subscriptions
    ]
