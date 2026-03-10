"""Book schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId

from models.book import BookStatus


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Name of the book")
    author: str = Field(..., min_length=1, max_length=300, description="Author of the book")
    description: str = Field(default="", max_length=2000, description="Description of the book")
    status: BookStatus = Field(default=BookStatus.AVAILABLE, description="Status of the book")
    year: int = Field(..., ge=0, le=datetime.now().year + 1, description="Year of the book")


class BookResponse(BaseModel):
    id: PydanticObjectId
    title: str
    author: str
    description: str
    status: BookStatus
    year: int


class PageBooks(BaseModel):
    """Page-based pagination response."""

    items: list[BookResponse]
    page: int = Field(..., description="Current page (1-based)")
    size: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
