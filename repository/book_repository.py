"""Book repository with Motor (async MongoDB)."""

from bson import ObjectId
from bson.errors import InvalidId

from motor.motor_asyncio import AsyncIOMotorCollection

from models.book import BookStatus


def _doc_to_item(doc: dict) -> dict:
    """Map MongoDB document to API item (id from _id)."""
    return {
        "id": doc["_id"],
        "title": doc["title"],
        "author": doc["author"],
        "description": doc.get("description") or "",
        "status": doc.get("status", BookStatus.AVAILABLE.value),
        "year": doc["year"],
    }


class BookRepository:
    """Repository for book data using Motor async collection."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    async def get_all(
        self,
        *,
        status: BookStatus | None = None,
        author: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[dict], int]:
        """Return (items, total_count) for page-based pagination."""
        if size < 1:
            size = 10
        size = min(size, 100)
        if page < 1:
            page = 1

        filter_query: dict = {}
        if status is not None:
            filter_query["status"] = status.value
        if author is not None and author.strip():
            filter_query["author"] = author.strip()

        is_desc = sort_order and sort_order.lower() == "desc"
        direction = -1 if is_desc else 1
        if sort_by == "title":
            sort_key = [("title", direction), ("_id", direction)]
        elif sort_by == "year":
            sort_key = [("year", direction), ("_id", direction)]
        else:
            sort_key = [("_id", direction)]

        total = await self._collection.count_documents(filter_query)
        skip = (page - 1) * size
        cursor_cur = (
            self._collection.find(filter_query)
            .sort(sort_key)
            .skip(skip)
            .limit(size)
        )
        docs = await cursor_cur.to_list(length=size)

        return [_doc_to_item(d) for d in docs], total

    async def get_by_id(self, book_id: ObjectId | str) -> dict | None:
        """Return a book by ID or None."""
        try:
            oid = ObjectId(book_id) if isinstance(book_id, str) else book_id
        except InvalidId:
            return None
        doc = await self._collection.find_one({"_id": oid})
        return _doc_to_item(doc) if doc else None

    async def add(self, book: dict) -> dict:
        """Add a book to the database. Returns the added book (with id from _id)."""
        doc = {
            "title": book["title"],
            "author": book["author"],
            "description": book.get("description") or "",
            "status": book.get("status", BookStatus.AVAILABLE.value),
            "year": book["year"],
        }
        result = await self._collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return _doc_to_item(doc)

    async def delete(self, book_id: ObjectId | str) -> bool:
        """Remove a book by ID. Returns True if removed, False if not found."""
        try:
            oid = ObjectId(book_id) if isinstance(book_id, str) else book_id
        except InvalidId:
            return False
        response = await self._collection.delete_one({"_id": oid})
        return response.deleted_count > 0
