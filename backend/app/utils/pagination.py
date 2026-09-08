from typing import TypeVar, Generic, Sequence, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int
    limit: int
    total: int
    total_pages: int

    @classmethod
    def create(cls, items: Sequence[T], total: int, page: int, limit: int):
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            items=list(items),
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        )
