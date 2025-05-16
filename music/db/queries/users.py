from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from db.models import *

async def get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    user = await session.scalar(query)
    return user

async def get_user_by_name(session: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    user = await session.scalar(query)
    return user

async def create_user(session: AsyncSession, user: User):
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {
        "id": user.id
    }

async def update_user_username(session: AsyncSession, user_id: int, new_username: str):
    query = update(User).where(User.id == user_id).values(username=new_username)
    await session.execute(query)
    await session.commit()

async def update_user_avatar(session: AsyncSession, user_id: int, new_avatar_url: str):
    query = update(User).where(User.id == user_id).values(avatar_url=new_avatar_url)
    await session.execute(query)
    await session.commit()

async def get_artist(session: AsyncSession, user_id: int):
    query = select(Artist).where(Artist.id == user_id)
    user = await session.scalar(query)
    return user

async def get_artist_by_name(session: AsyncSession, username: str):
    query = select(Artist).where(Artist.username == username)
    user = await session.scalar(query)
    return user

async def create_artist(session: AsyncSession, user: Artist):
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {
        "id": user.id
    }

async def update_artist_username(session: AsyncSession, user_id: int, new_username: str):
    query = update(Artist).where(Artist.id == user_id).values(username=new_username)
    await session.execute(query)
    await session.commit()

async def update_artist_avatar(session: AsyncSession, user_id: int, new_avatar_url: str):
    query = update(Artist).where(Artist.id == user_id).values(avatar_url=new_avatar_url)
    await session.execute(query)
    await session.commit()
