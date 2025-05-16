from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete, and_

from db.models import *

async def create_subscribe(
    session: AsyncSession,
    subscribe: Subscribe
):
    session.add(subscribe)
    try:
        await session.commit()
        await session.refresh(subscribe)
        return {"status": "subscribed"}
    except IntegrityError:
        await session.rollback()
        return {"status": "already subscribed"}

async def delete_subscribe(
    session: AsyncSession,
    subscribe: Subscribe
):
    query = delete(Subscribe).where(
        and_(
            Subscribe.user_id == subscribe.user_id,
            Subscribe.artist_id == subscribe.artist_id
        )
    )
    await session.execute(query)
    await session.commit()

async def get_user_subscriptions(
    session: AsyncSession,
    user_id: int,
    limit: int = 10,
    offset: int = 0
):
    query = (
        select(Subscribe, Artist)
        .join(Artist, Subscribe.artist_id == Artist.id)
        .where(Subscribe.user_id == user_id)
        .order_by(Subscribe.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return result.all()
