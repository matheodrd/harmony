from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models import Channel, Server, User
from app.security import password_hash

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import ChannelCreate, ServerCreate, UserCreate


async def get_all_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User))
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    user = User(
        username=payload.username,
        hashed_password=password_hash.hash(payload.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def create_server(
    db: AsyncSession, payload: ServerCreate, owner_id: int
) -> Server:
    server = Server(
        name=payload.name,
        owner_id=owner_id,
    )

    db.add(server)
    await db.commit()
    await db.refresh(server)

    return server


async def get_server_by_id(db: AsyncSession, server_id: int) -> Server | None:
    return await db.get(Server, server_id)


async def create_channel(
    db: AsyncSession, payload: ChannelCreate, server_id: int
) -> Channel:
    channel = Channel(
        name=payload.name,
        type=payload.type,
        server_id=server_id,
    )

    db.add(channel)
    await db.commit()
    await db.refresh(channel)

    return channel
