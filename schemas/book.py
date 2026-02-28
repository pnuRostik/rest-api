"""Book schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from models.book import BookStatus


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Name of the book")
    author: str = Field(..., min_length=1, max_length=300, description="Author of the book")
    description: str = Field(default="", max_length=2000, description="Description of the book")
    status: BookStatus = Field(default=BookStatus.AVAILABLE, description="Status of the book")
    year: int = Field(..., ge=0, le=datetime.now().year + 1, description="Year of the book")

