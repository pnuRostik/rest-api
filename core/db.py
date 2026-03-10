import os

import motor.motor_asyncio

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongo_admin:password@localhost:27017",
)
DATABASE_NAME = os.getenv("MONGO_DATABASE", "books")

client: motor.motor_asyncio.AsyncIOMotorClient | None = None


def get_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    """Return the global Motor client (create on first use)."""
    global client
    if client is None:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    return client


def get_database():
    """Return the books database."""
    return get_client()[DATABASE_NAME]


def get_books_collection():
    """Return the books collection."""
    return get_database()["books"]


async def get_db():
    """Dependency that yields the books collection."""
    yield get_books_collection()


async def close_client():
    """Close the Motor client (e.g. on app shutdown)."""
    global client
    if client is not None:
        client.close()
        client = None
