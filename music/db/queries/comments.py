from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from db.models import *

async def create_comment(
    session: AsyncSession,
    comment: Comment
) -> dict:
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return {"id": comment.id}

async def delete_comment(
    session: AsyncSession,
    comment_id: int,
    user_id: int
) -> dict:
    query = delete(Comment).where(
        and_(
            Comment.id == comment_id,
            Comment.user_id == user_id
        )
    )
    await session.execute(query)
    await session.commit()

async def get_track_comments(
    session: AsyncSession,
    track_id: int,
    limit: int = 10,
    offset: int = 0
) -> list[tuple[Comment, User]]:
    query = (
        select(Comment, User)
        .join(User, Comment.user_id == User.id)
        .where(Comment.track_id == track_id)
        .order_by(Comment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return result.all()
