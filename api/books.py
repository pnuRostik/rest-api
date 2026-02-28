from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from models.book import BookStatus
from repository.book_repository import BookRepository
from schemas.book import BookCreate, PaginatedBooks
from services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"])


def get_book_repository(db: AsyncSession = Depends(get_db)) -> BookRepository:
    return BookRepository(db)


def get_book_service(repo: BookRepository = Depends(get_book_repository)) -> BookService:
    return BookService(repo)


@router.get(
    "",
    response_model=PaginatedBooks,
    status_code=200,
    summary="Get all books",
    description="Get all books with optional filtering by status/author, sorting and pagination.",
)
async def get_books(
    service: BookService = Depends(get_book_service),
    status: BookStatus | None = Query(None, description="Filter by status"),
    author: str | None = Query(None, description="Filter by author (exact match)"),
    sort_by: str | None = Query(None, description="Sort by: title, year"),
    sort_order: str = Query("asc", description="Sort order: asc, desc"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """Return paginated books. 200 OK."""
    if sort_by is not None and sort_by not in ("title", "year"):
        raise HTTPException(status_code=400, detail="sort_by must be 'title' or 'year'")
    data = await service.get_all(
        status=status,
        author=author,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return PaginatedBooks(**data)


@router.get(
    "/{book_id}",
    status_code=200,
    summary="Get book by UUID",
)
async def get_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service),
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
    service: BookService = Depends(get_book_service),
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
    service: BookService = Depends(get_book_service),
):
    await service.delete(book_id)
