from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.db.models.notification import NotificationCategory


class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    category: NotificationCategory = NotificationCategory.SYSTEM
    target_route: Optional[str] = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    message: str
    category: NotificationCategory
    target_route: Optional[str] = None
    is_read: bool
    created_at: datetime

