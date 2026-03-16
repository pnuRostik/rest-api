from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from pydantic_mongo import ObjectIdField


class BookStatus(str, Enum):
    available = "available"
    issued = "issued"

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: BookStatus = Field(default=BookStatus.available)
    year: int = Field(..., gt=0)

    # Зберігаємо enum як строку в БД
    model_config = ConfigDict(use_enum_values=True)


class BookResponse(BaseModel):
   
    id: ObjectIdField = Field(alias="_id")
    title: str
    author: str
    description: Optional[str] = None
    status: str
    year: int

    model_config = ConfigDict(populate_by_name=True)