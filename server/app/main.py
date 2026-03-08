from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException, status

from app import crud
from app.database import engine
from app.dependencies import DBSessionDep  # noqa: TC001
from app.models import Base
from app.schemas import UserCreate, UserRead

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from app.models import User


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
