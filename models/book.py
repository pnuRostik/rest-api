"""Book status enum (MongoDB documents are plain dicts)."""

from enum import Enum


class BookStatus(str, Enum):
    """Book status in the library."""

    AVAILABLE = "available"
    BORROWED = "borrowed"
