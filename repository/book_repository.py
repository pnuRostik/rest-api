"""Book repository with SQLAlchemy async session (PostgreSQL)."""

from uuid import UUID

from sqlalchemy import select, func, asc, desc
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
        sort_by: str | None = None,
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[dict], int]:
        """Return paginated books with optional filter and sort. Returns (items, total)."""
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        page_size = min(page_size, 100)

        base = select(Book)
        count_stmt = select(func.count()).select_from(Book)

        if status is not None:
            base = base.where(Book.status == status)
            count_stmt = count_stmt.where(Book.status == status)

        if author is not None and author.strip():
            author_trimmed = author.strip()
            base = base.where(Book.author == author_trimmed)
            count_stmt = count_stmt.where(Book.author == author_trimmed)

        SORT_FIELDS = {
            "title": Book.title,
            "year": Book.year,
            "author": Book.author,
        }

        if sort_by:
            order_col = SORT_FIELDS.get(sort_by, Book.id)
            if sort_order.lower() == "desc":
                base = base.order_by(desc(order_col))
            else:
                base = base.order_by(asc(order_col))
        else:
            base = base.order_by(Book.id)


        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        base = base.offset(offset).limit(page_size)
        result = await self._session.execute(base)
        books = result.scalars().all()

        return [_book_to_dict(b) for b in books], total

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
