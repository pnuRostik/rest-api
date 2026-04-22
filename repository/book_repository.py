"""Book repository with SQLAlchemy async session (PostgreSQL)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from models.book import Book, BookStatus


def _book_to_dict(book: Book) -> dict:
    """Map Book ORM to dict for API response."""
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "description": book.description or "",
        "status": book.status.value if hasattr(book.status, "value") else book.status,
        "year": book.year,
    }


class BookRepository:
    """Repository for book data using async SQLAlchemy session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(
        self,
        *,
        status: BookStatus | None = None,
        author: str | None = None,
        cursor: datetime | None = None,
        limit: int = 10,
    ) -> tuple[list[dict], datetime | None]:
        if limit < 1:
            limit = 10
        limit = min(limit, 100)
        fetch_limit = limit + 1

        base = select(Book)

        if status is not None:
            base = base.where(Book.status == status)

        if author is not None and author.strip():
            base = base.where(Book.author == author.strip())

        base = base.order_by(asc(Book.created_at), asc(Book.id))

        if cursor is not None:
            base = base.where(Book.created_at > cursor)

        base = base.limit(fetch_limit)
        result = await self._session.execute(base)
        books = result.scalars().all()

        has_next = len(books) > limit
        items = books[:limit]
        next_cursor = items[-1].created_at if has_next and items else None

        return [_book_to_dict(b) for b in items], next_cursor

    async def get_by_id(self, book_id: UUID) -> dict | None:
        """Return a book by ID or None."""
        stmt = select(Book).where(Book.id == book_id)
        result = await self._session.execute(stmt)
        book = result.scalar_one_or_none()
        return _book_to_dict(book) if book else None

    async def add(self, book: dict) -> dict:
        """Add a book to the database. Returns the added book (with id)."""
        status_val = book.get("status")
        if isinstance(status_val, str):
            status_val = BookStatus(status_val)
        entity = Book(
            id=book.get("id"),
            title=book["title"],
            author=book["author"],
            description=book.get("description") or "",
            status=status_val or BookStatus.AVAILABLE,
            year=book["year"],
        )
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return _book_to_dict(entity)

    async def delete(self, book_id: UUID) -> bool:
        """Remove a book by ID. Returns True if removed, False if not found."""
        stmt = select(Book).where(Book.id == book_id)
        result = await self._session.execute(stmt)
        book = result.scalar_one_or_none()
        if book is None:
            return False
        await self._session.delete(book)
        await self._session.commit()
        return True
