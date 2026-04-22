import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5439/library")

_is_testing = os.getenv("TESTING") == "1"
_engine_kwargs: dict = {"echo": not _is_testing}
if _is_testing:
    # TestClient runs the ASGI app in a thread; asyncpg + default pool often hits
    # "cannot perform operation: another operation is in progress".
    _engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session