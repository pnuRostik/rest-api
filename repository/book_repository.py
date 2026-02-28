"""In-memory book storage (List[Dict])."""

from uuid import UUID

from models.book import BookStatus


class BookRepository:
    """Repository for book data (in-memory List[Dict])."""

    def __init__(self) -> None:
        self._storage: list[dict] = []

    async def get_all(
        self,
        *,
        status: BookStatus | None = None,
        author: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> list[dict]:
        """Return all books with optional filter and sort."""
        result = list(self._storage)

        if status is not None:
            status_val = status.value if hasattr(status, "value") else status
            result = [b for b in result if b.get("status") == status_val]

        if author is not None and author.strip():
            author_lower = author.strip().lower()
            result = [b for b in result if (b.get("author") or "").lower() == author_lower]

        if sort_by:
            reverse = sort_order.lower() == "desc"
            if sort_by == "title":
                result = sorted(result, key=lambda b: (b.get("title") or "").lower(), reverse=reverse)
            elif sort_by == "year":
                result = sorted(result, key=lambda b: b.get("year", 0), reverse=reverse)
            else:
                result = sorted(result, key=lambda b: str(b.get("id", "")), reverse=reverse)

        return result

    async def get_by_id(self, book_id: UUID) -> dict | None:
        """Return a book by ID or None."""
        for book in self._storage:
            if str(book.get("id")) == str(book_id):
                return book
        return None

    async def add(self, book: dict) -> dict:
        """Add a book to storage. Returns the added book (with id)."""
        self._storage.append(book)
        return book

    async def delete(self, book_id: UUID) -> bool:
        """Remove a book by ID. Returns True if removed, False if not found."""
        for i, book in enumerate(self._storage):
            if str(book.get("id")) == str(book_id):
                self._storage.pop(i)
                return True
        return False
