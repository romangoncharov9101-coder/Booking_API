from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}

class ErrorResponse(BaseModel):
    error: ErrorDetail

class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    model_config = {'from_attributes': True}

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> 'PaginatedResponse[T]':
        pages = (total + page_size - 1)
        return cls(items=items, total=total, page=page, page_size=page_size, pages=pages)