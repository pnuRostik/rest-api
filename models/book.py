"""Book model and status enum."""

from enum import Enum


class BookStatus(str, Enum):
    """Book status in the library."""

    AVAILABLE = "available"  
    BORROWED = "borrowed" 
