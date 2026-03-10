from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.books import router as books_router
from core.db import close_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_client()


app = FastAPI(
    title="Library API",
    description="API : Book.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(books_router)
