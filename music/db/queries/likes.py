from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete, and_

from db.models import *

async def create_like(
    session: AsyncSession,
    like: Like
) -> dict:
    session.add(like)
    try:
        await session.commit()
        await session.refresh(like)
        return {"status": "liked"}
    except IntegrityError:
        await session.rollback()
        return {"status": "already liked"}

async def delete_like(
    session: AsyncSession,
    like: Like
) -> dict:
    query = delete(Like).where(
        and_(
            Like.user_id == like.user_id,
            Like.track_id == like.track_id
        )
    )
    await session.execute(query)
    await session.commit()

async def get_user_likes(
    session: AsyncSession,
    user_id: int,
    limit: int = 10,
    offset: int = 0
) -> list[tuple[Like, Track, Artist]]:
    query = (
        select(Like, Track, Artist)
        .join(Track, Like.track_id == Track.id)
        .join(Artist, Track.artist_id == Artist.id)
        .where(Like.user_id == user_id)
        .order_by(Like.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return result.all()
