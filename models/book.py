"""Book model and status enum."""

from enum import Enum
import uuid
from sqlalchemy import Column, String, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from core.db import Base


class BookStatus(str, Enum):
    """Book status in the library."""

    AVAILABLE = "available"  
    BORROWED = "borrowed" 



class Book(Base):
    __tablename__ = "books"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(BookStatus), nullable=False, default=BookStatus.AVAILABLE)
    year = Column(Integer, nullable=False)