from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException, status

from app import crud
from app.database import engine
from app.dependencies import CurrentUserDep, DBSessionDep, OAuth2FormDep  # noqa: TC001
from app.models import Base
from app.schemas import (
    ChannelCreate,
    ChannelRead,
    ServerCreate,
    ServerRead,
    Token,
    UserCreate,
    UserRead,
)
from app.security import create_access_token, password_hash

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from app.models import Channel, Server, User


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    # TODO: use proper DB migration system (alembic?)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(title="Harmony", lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello from Harmony :P"}


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: DBSessionDep) -> User:
    existing_user = await crud.get_user_by_username(db, payload.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{payload.username}' is already taken",
        )
    return await crud.create_user(db, payload)


@app.get("/users", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_users(db: DBSessionDep) -> list[User]:
    return await crud.get_all_users(db)


@app.get("/users/me", response_model=UserRead)
async def get_me(current_user: CurrentUserDep) -> User:
    return current_user


@app.get("/users/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: DBSessionDep) -> User:
    user = await crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


@app.post("/servers", response_model=ServerRead, status_code=status.HTTP_201_CREATED)
async def create_server(
    payload: ServerCreate, db: DBSessionDep, current_user: CurrentUserDep
) -> Server:
    return await crud.create_server(db, payload, owner_id=current_user.id)


@app.post(
    "/servers/{server_id}/channels",
    response_model=ChannelRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_channel(
    server_id: int,
    payload: ChannelCreate,
    db: DBSessionDep,
    current_user: CurrentUserDep,
) -> Channel:
    server = await crud.get_server_by_id(db, server_id)
    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server {server_id} not found",
        )
    if current_user.id != server.owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not server {server_id} owner",
        )

    return await crud.create_channel(db, payload, server_id)


@app.post("/auth/token")
async def login(form_data: OAuth2FormDep, db: DBSessionDep) -> Token:
    user = await crud.get_user_by_username(db, form_data.username)
    if user is None or not password_hash.verify(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(subject=user.username))
