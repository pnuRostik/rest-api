from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from models.book import BookStatus
from schemas.book import BookCreate
from services.book_service import BookService
from repository.book_repository import BookRepository

router = APIRouter(prefix="/books", tags=["books"])

repo = BookRepository()
service = BookService(repo)

@router.get(
    "",
    status_code=200,
    summary="Get all books",
    description="Get all books with optional filtering by status/author and sorting by title/year.",
)
async def get_books(
    status: BookStatus | None = Query(None, description="Filter by status"),
    author: str | None = Query(None, description="Filter by author (exact match)"),
    sort_by: str | None = Query(None, description="Sort by: title, year"),
    sort_order: str = Query("asc", description="Sort order: asc, desc"),
):
    """Return all books. 200 OK."""
    if sort_by is not None and sort_by not in ("title", "year"):
        raise HTTPException(status_code=400, detail="sort_by must be 'title' or 'year'")
    return await service.get_all(
        status=status,
        author=author,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{book_id}",
    status_code=200,
    summary="Get book by UUID",
)
async def get_book(
    book_id: UUID,
):
    book = await service.get_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post(
    "",
    status_code=201,
    summary="Add a book",
)
async def create_book(
    payload: BookCreate,
):
    """Create a new book. 201 Created with the created book (including generated UUID)."""
    return await service.create(payload)


@router.delete(
    "/{book_id}",
    status_code=204,
    summary="Delete a book (idempotent)",
)
async def delete_book(
    book_id: UUID,
):
    await service.delete(book_id)
