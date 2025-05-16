from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from db.models import Album, AlbumTrack, Track

async def create_album(session: AsyncSession, album: Album):
    session.add(album)
    await session.commit()
    await session.refresh(album)
    return {"id": album.id}

async def get_albums(
    session: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    album_type: str | None = None
):
    query = select(Album)
    if album_type:
        query = query.where(Album.type == album_type)
    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    return result.scalars().all()

async def get_album_with_tracks(session: AsyncSession, album_id: int):
    album_query = select(Album).where(Album.id == album_id)
    album = await session.scalar(album_query)
    if not album:
        return None
    tracks_query = (
        select(Track)
        .join(AlbumTrack, AlbumTrack.track_id == Track.id)
        .where(AlbumTrack.album_id == album_id)
    )
    result = await session.execute(tracks_query)
    tracks = result.scalars().all()
    return {
        "album": album,
        "tracks": tracks
    }

async def add_track_to_album(
    session: AsyncSession,
    album_id: int,
    track_id: int
):
    album_track = AlbumTrack(album_id=album_id, track_id=track_id)
    session.add(album_track)
    await session.commit()
    return {"status": f"track {track_id} added to album {album_id}"}

async def remove_track_from_album(
    session: AsyncSession,
    album_id: int,
    track_id: int
):
    query = delete(AlbumTrack).where(
        and_(
            AlbumTrack.album_id == album_id,
            AlbumTrack.track_id == track_id
        )
    )
    await session.execute(query)
    await session.commit()
    return {"status": f"track {track_id} removed from album {album_id}"}

async def delete_album(session: AsyncSession, album_id: int):
    delete_tracks_query = delete(AlbumTrack).where(AlbumTrack.album_id == album_id)
    await session.execute(delete_tracks_query)
    delete_album_query = delete(Album).where(Album.id == album_id)
    await session.execute(delete_album_query)
    await session.commit()
    return {"status": f"album {album_id} and all its tracks relations deleted"}
