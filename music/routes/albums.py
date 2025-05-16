from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from session import get_session
from clients import auth
from db import queries
from db.models import Album

api_router = APIRouter()
security = HTTPBearer()

class CreateAlbumRequest(BaseModel):
    title: str
    cover_image_url: str

class AddTrackToAlbumRequest(BaseModel):
    track_id: int


@api_router.post("/albums")
async def create_album(
    album_data: CreateAlbumRequest,
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

    album_type = "album" if role == "artist" else "playlist"

    if role == "artist":
        db_user = await queries.get_artist_by_name(session, username)
    else:
        db_user = await queries.get_user_by_name(session, username)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_album = Album(
        user_id=db_user.id,
        title=album_data.title,
        cover_image_url=album_data.cover_image_url,
        type=album_type
    )

    return await queries.create_album(session, db_album)


@api_router.get("/albums")
async def get_albums(
    type: str | None = Query(None, description="Filter by album type (album/playlist)"),
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

    albums = await queries.get_albums(
        session,
        limit=limit,
        offset=offset,
        album_type=type
    )

    return {
        "albums": [
            {
                "id": album.id,
                "title": album.title,
                "cover_image_url": album.cover_image_url,
                "type": album.type,
                "release_date": album.release_date.isoformat() if album.release_date else None
            } for album in albums
        ]
    }

@api_router.get("/albums/{album_id}")
async def get_album(
    album_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    client = auth.AuthClient()
    auth_response = await client.validate_token(token)
    if not auth_response:
        raise HTTPException(status_code=401, detail="Incorrect token")

    album_data = await queries.get_album_with_tracks(session, album_id)
    if not album_data:
        raise HTTPException(status_code=404, detail="Album not found")

    return {
        "album": {
            "id": album_data["album"].id,
            "title": album_data["album"].title,
            "cover_image_url": album_data["album"].cover_image_url,
            "type": album_data["album"].type,
            "release_date": album_data["album"].release_date.isoformat(),
            "user_id": album_data["album"].user_id
        },
        "tracks": [
            {
                "id": track.id,
                "title": track.title,
                "duration": track.duration,
                "file_url": track.file_url
            } for track in album_data["tracks"]
        ]
    }

@api_router.delete("/albums/{album_id}")
async def delete_album(
    album_id: int,
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

    if role == "artist":
        db_user = await queries.get_artist_by_name(session, username)
    else:
        db_user = await queries.get_user_by_name(session, username)
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    album_data = await queries.get_album_with_tracks(session, album_id)
    if not album_data:
        raise HTTPException(status_code=404, detail="Album not found")

    if album_data["album"].user_id != db_user.id:
        raise HTTPException(status_code=403, detail="Not the album owner")

    await queries.delete_album(session, album_id)


@api_router.post("/albums/{album_id}/tracks")
async def add_track_to_album(
    album_id: int,
    track_data: AddTrackToAlbumRequest,
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

    if role == "artist":
        db_user = await queries.get_artist_by_name(session, username)
    else:
        db_user = await queries.get_user_by_name(session, username)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    album_data = await queries.get_album_with_tracks(session, album_id)
    if not album_data:
        raise HTTPException(status_code=404, detail="Album not found")

    if album_data["album"].user_id != db_user.id:
        raise HTTPException(status_code=403, detail="Not the album owner")

    db_track = await queries.get_track(session, track_data.track_id)
    if not db_track:
        raise HTTPException(status_code=404, detail="Track not found")

    await queries.add_track_to_album(session, album_id, track_data.track_id)


@api_router.delete("/albums/{album_id}/tracks/{track_id}")
async def remove_track_from_album(
    album_id: int,
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

    if role == "artist":
        db_user = await queries.get_artist_by_name(session, username)
    else:
        db_user = await queries.get_user_by_name(session, username)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    album_data = await queries.get_album_with_tracks(session, album_id)
    if not album_data:
        raise HTTPException(status_code=404, detail="Album not found")

    if album_data["album"].user_id != db_user.id:
        raise HTTPException(status_code=403, detail="Not the album owner")

    tracks_in_album = [track.id for track in album_data["tracks"]]
    if track_id not in tracks_in_album:
        raise HTTPException(status_code=404, detail="Track not found in album")

    await queries.remove_track_from_album(session, album_id, track_id)
