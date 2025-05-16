from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from clients import sample, auth
from db.models import Comment
from db import queries

api_router = APIRouter()
security = HTTPBearer()

@api_router.post("/tracks/{track_id}/comments")
async def create_comment(
    track_id: int,
    comment_data: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> dict:
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    if auth_response["role"] == "artist":
        raise HTTPException(status_code=403, detail="Artists cannot send a comments")

    db_user = await queries.get_user_by_name(session, auth_response["username"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_track = await queries.get_track(session, track_id)
    if not db_track:
        raise HTTPException(status_code=404, detail="Track not found")

    comment = Comment(
        user_id=db_user.id,
        track_id=track_id,
        text=comment_data
    )

    return await queries.create_comment(session, comment)


@api_router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    db_user = await queries.get_user_by_name(session, auth_response["username"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await queries.delete_comment(session, comment_id, db_user.id)


@api_router.get("/tracks/{track_id}/comments")
async def get_track_comments(
    track_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    db_track = await queries.get_track(session, track_id)
    if not db_track:
        raise HTTPException(status_code=404, detail="Track not found")

    comments = await queries.get_track_comments(
        session,
        track_id=track_id,
        limit=limit,
        offset=offset
    )

    return [
        {
            "id": comment.id,
            "text": comment.text,
            "created_at": comment.created_at,
            "user": {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url
            }
        } for comment, user in comments
    ]
