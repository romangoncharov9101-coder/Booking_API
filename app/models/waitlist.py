import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.venue import Venue
    from app.models.notification import NotificationEvent

class WaitlistStatus(str, enum.Enum):
    ACTIVE = 'active'
    NOTIFIED = 'notified'
    BOOKED = 'booked'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'

class WaitlistEntry(BaseModel):
    __tablename__ = 'waitlist_entries'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('venues.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('services.id', ondelete='SET NULL'), nullable=True)
    preferred_date_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    preferred_date_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    min_notice_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    status: Mapped[WaitlistStatus] = mapped_column (
        Enum(WaitlistStatus, name='waitlist_status'),
        nullable=False,
        default=WaitlistStatus.ACTIVE,
        index=True,
    )
    user: Mapped['User'] = relationship(back_populates='waitlist_entries', lazy='noload')
    venue: Mapped['Venue'] = relationship(back_populates='waitlist_entries', lazy='noload')
    notifications: Mapped[list['NotificationEvent']] = relationship(back_populates='waitlist_entry', lazy='noload')

    __table_args__ = (
        Index('idx_waitlist_venue_id', 'venue_id'),
        Index('idx_waitlist_user_id', 'user_id'),
        Index('idx_waitlist_status', 'status'),
        Index('idx_waitlist_period', 'preferred_date_from', 'preferred_date_to'),
    )