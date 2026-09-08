from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.db.models.user import UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: Optional[str] = None
    phone: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

