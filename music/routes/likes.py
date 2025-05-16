from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from clients import sample, auth
from db.models import Like
from db import queries

api_router = APIRouter()
security = HTTPBearer()


@api_router.post("/tracks/{track_id}/like")
async def like_track(
    track_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    if auth_response["role"] == "artist":
        raise HTTPException(status_code=403, detail="Only users can like tracks")

    db_user = await queries.get_user_by_name(session, auth_response["username"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_track = await queries.get_track(session, track_id)
    if not db_track:
        raise HTTPException(status_code=404, detail="Track not found")

    like = Like(user_id=db_user.id, track_id=track_id)

    return await queries.create_like(session, like)


@api_router.delete("/tracks/{track_id}/like")
async def unlike_track(
    track_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    if auth_response["role"] == "artist":
        raise HTTPException(status_code=403, detail="Artists cannot unlike tracks")

    db_user = await queries.get_user_by_name(session, auth_response["username"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    like = Like(user_id=db_user.id, track_id=track_id)
    await queries.delete_like(session, like)


@api_router.get("/users/me/likes")
async def get_user_likes(
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
        raise HTTPException(status_code=403, detail="Artists cannot have likes")

    db_user = await queries.get_user_by_name(session, auth_response["username"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    likes = await queries.get_user_likes(
        session,
        user_id=db_user.id,
        limit=limit,
        offset=offset
    )

    return [
        {
            "track": {
                "id": track.id,
                "title": track.title,
                "duration": track.duration,
                "file_url": track.file_url,
                "created_at": track.created_at,
                "artist": {
                    "id": artist.id,
                    "username": artist.username,
                    "avatar_url": artist.avatar_url
                }
            },
            "liked_at": like.created_at.isoformat()
        }
        for like, track, artist in likes
    ]
