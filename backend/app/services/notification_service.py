from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.core.exceptions import NotFoundException


class NotificationService:
    @staticmethod
    def create(db: Session, data: NotificationCreate) -> Notification:
        notif = Notification(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            category=data.category,
            target_route=data.target_route,
            is_read=False,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def get_user_notifications(db: Session, user_id: str) -> List[Notification]:
        return list(
            db.scalars(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(desc(Notification.created_at))
            ).all()
        )

    @staticmethod
    def mark_as_read(db: Session, notification_id: str, user_id: str) -> Notification:
        notif = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id))
        if not notif:
            raise NotFoundException("Notification", notification_id)
        notif.is_read = True
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def mark_all_as_read(db: Session, user_id: str) -> int:
        notifs = db.scalars(select(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False))).all()
        for n in notifs:
            n.is_read = True
        db.commit()
        return len(notifs)
