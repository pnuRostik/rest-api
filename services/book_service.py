"""Book business logic."""

from uuid import UUID, uuid4

from models.book import BookStatus
from repository.book_repository import BookRepository
from schemas.book import BookCreate


class BookService:
    """Service for book operations."""

    def __init__(self, repository: BookRepository) -> None:
        self._repo = repository

    async def get_all(
        self,
        *,
        status: BookStatus | None = None,
        author: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        cursor: UUID | None = None,
        limit: int = 10,
    ) -> dict:
        """Get books with cursor-based pagination."""
        items, next_cursor = await self._repo.get_all(
            status=status,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            cursor=cursor,
            limit=limit,
        )
        return {
            "items": items,
            "next_cursor": next_cursor,
            "limit": limit,
        }

    async def get_by_id(self, book_id: UUID) -> dict | None:
        """Get a book by ID."""
        return await self._repo.get_by_id(book_id)

    async def create(self, payload: BookCreate) -> dict:
        """Create a new book (ID generated as UUID)."""
        book_id = uuid4()
        book_dict = {
            "id": book_id,
            "title": payload.title,
            "author": payload.author,
            "description": payload.description,
            "status": payload.status.value,
            "year": payload.year,
        }
        return await self._repo.add(book_dict)

    async def delete(self, book_id: UUID) -> bool:
        """Delete a book by ID."""
        return await self._repo.delete(book_id)
