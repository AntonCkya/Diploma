from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from db.models import User, Token

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

async def save_token(session: AsyncSession, token: Token):
    session.add(token)
    await session.commit()

async def delete_token(session: AsyncSession, user_id: str):
    query = delete(Token).where(Token.user_id == int(user_id))
    await session.execute(query)
    await session.commit()

async def check_token(session: AsyncSession, str_token: str):
    query = select(Token).where(Token.token == str_token)
    token = await session.scalar(query)
    return token

async def update_user(session: AsyncSession, user: User):
    session.add(user)
    await session.commit()
