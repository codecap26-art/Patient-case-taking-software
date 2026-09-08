from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.notification import NotificationResponse
from app.schemas.common import StatusResponse
from app.services.notification_service import NotificationService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
@router.get("/my-notifications", response_model=List[NotificationResponse])
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NotificationService.get_user_notifications(db, current_user.id)


@router.post("/{id}/read", response_model=NotificationResponse)
def mark_notification_read(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NotificationService.mark_as_read(db, id, current_user.id)


@router.post("/read-all", response_model=StatusResponse)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = NotificationService.mark_all_as_read(db, current_user.id)
    return StatusResponse(message=f"Marked {count} notifications as read.")
