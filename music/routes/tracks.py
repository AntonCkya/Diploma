from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from session import get_session
from clients import sample, auth
from db.models import Track
from db import queries

api_router = APIRouter()
security = HTTPBearer()

@api_router.post("/tracks/")
async def create_track(
    title: str,
    duration: int,
    file: UploadFile,
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

    if role != "artist":
        raise HTTPException(status_code=400, detail="Incorrect user")

    db_user = await queries.get_artist_by_name(session, username)
    db_track = Track(
        title = title,
        duration = duration,
        file_url = f'http://localhost:8004/stream/{file.filename.replace('.mp3', '')}/playlist.m3u8',
        artist_id = db_user.id
    )

    preproc = sample.PreprocessingClient()
    proc_id = (await preproc.upload_audio(file))["id"]
    track_id = (await queries.create_track(session, db_track))["id"]

    return {
        "track_id": track_id,
        "process_id": proc_id
    }


@api_router.get("/tracks/{track_id}")
async def get_track(
    track_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")
    
    db_track = await queries.get_track(session, track_id)

    if not db_track:
        raise HTTPException(status_code=404, detail="Track not founded")

    return {
        "title": db_track.title,
        "duration": db_track.duration,
        "file_url": db_track.file_url,
        "artist_id": db_track.artist_id,
        "created_at": db_track.created_at
    }


@api_router.delete("/tracks/{track_id}")
async def delete_track(
    track_id: int,
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

    if role != "artist":
        raise HTTPException(status_code=400, detail="Incorrect user")

    db_user = await queries.get_artist_by_name(session, username)
    db_track = await queries.get_track(session, track_id)

    if db_user.id != db_track.artist_id:
        raise HTTPException(status_code=403, detail="Incorrect user")

    await queries.delete_track(session, track_id)

@api_router.get("/tracks")
async def get_tracks(
    title: str | None = Query(None),
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

    tracks = await queries.get_tracks(
        session,
        limit=limit,
        offset=offset,
        search_title=title
    )

    return [
        {
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
        }
        for track, artist in tracks
    ]
