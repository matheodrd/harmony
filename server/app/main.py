from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from app.database import engine
from app.models import Base

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


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
