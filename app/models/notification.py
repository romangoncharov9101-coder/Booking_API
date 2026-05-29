import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.waitlist import WaitlistEntry

class NotificationType(str, enum.Enum):
    SLOT_AVAILABLE = 'slot_available'
    BOOKING_CONFIRMED = 'booking_confirmed'
    BOOKING_CANCELLED = 'booking_cancelled'
    BOOKING_REMINDER = 'booking_reminder'
    VENUE_BOOKING_CANCELLED = 'venue_booking_cancelled'
    WAITLIST_EXPIRED = 'waitlist_expired'
    EMAIL_VERIFICATION = 'email_verification'
    PASSWORD_RESET = 'password_reset'

class NotificationChannel(str, enum.Enum):
    EMAIL = 'email'

class NotificationStatus(str, enum.Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'

class NotificationEvent(BaseModel):
    __tablename__ = 'notification_events'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    venue_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('venues.id', ondelete='SET NULL'), nullable=True)
    waitlist_entry_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('waitlist_entries.id', ondelete='SET NULL'), nullable=True)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType, name='notification_type'), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel, name='notification_channel'), nullable=False, default=NotificationChannel.EMAIL)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus, name='notification_status'), nullable=False, default=NotificationStatus.PENDING, index=True)
    error_message: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped['User'] = relationship(back_populates='notifications', lazy='noload')
    waitlist_entry: Mapped['WaitlistEntry | None'] = relationship(back_populates='notifications', lazy='noload')

    __table_args__ = (
        Index('idx_notification_status', 'status'),
        Index('idx_notification_user_id', 'user_id'),
        Index('idx_notification_type', 'type'),
    )

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'

    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    meta: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index('idx_audit_log_actor_id', 'actor_id'),
        Index('idx_audit_log_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_log_created_at', 'created_at'),
    )