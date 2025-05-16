from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from db.models import *

async def create_track(session: AsyncSession, track: Track):
    session.add(track)
    await session.commit()
    await session.refresh(track)
    return {
        "id": track.id
    }

async def get_track(session: AsyncSession, track_id: int):
    query = select(Track).where(Track.id == track_id)
    user = await session.scalar(query)
    return user

async def delete_track(session: AsyncSession, track_id: int):
    query = delete(Track).where(Track.id == track_id)
    await session.execute(query)
    await session.commit()

async def get_tracks(
    session: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    search_title: str | None = None
):
    query = (
        select(Track, Artist)
        .join(Artist, Track.artist_id == Artist.id)
        .order_by(Track.created_at.desc())
    )
    if search_title:
        query = query.where(Track.title.ilike(f"%{search_title}%"))
    
    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    return result.all()
