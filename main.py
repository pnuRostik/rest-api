from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.books import router as books_router
from core.db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Library API",
    description="API : Book.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(books_router)


