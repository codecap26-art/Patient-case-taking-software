from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.db.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.core.dependencies import require_role
from app.utils.pagination import PaginatedParams, PaginatedResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_users(
    pagination: PaginatedParams = Depends(),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(User).count()) if hasattr(select(User), "count") else len(db.scalars(select(User)).all())
    users = db.scalars(select(User).offset(pagination.offset).limit(pagination.limit)).all()
    return PaginatedResponse.create(users, total, pagination.page, pagination.limit)
