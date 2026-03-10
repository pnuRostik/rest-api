import os

import pymongo

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongo_admin:password@localhost:27017",
)
DATABASE_NAME = os.getenv("MONGO_DATABASE", "books")

_client: pymongo.MongoClient | None = None


def get_client() -> pymongo.MongoClient:
    """Return the global PyMongo client (create on first use)."""
    global _client
    if _client is None:
        _client = pymongo.MongoClient(MONGO_URI)
    return _client


def get_database():
    """Return the books database."""
    return get_client()[DATABASE_NAME]


def get_books_collection():
    """Return the books collection."""
    return get_database()["books"]


def close_client() -> None:
    """Close the global MongoDB client (for app teardown)."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
