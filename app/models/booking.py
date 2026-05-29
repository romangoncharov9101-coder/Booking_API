import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import DDL

from app.db.base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.venue import Venue, Service, Resource
    from app.models.review import Review

class BookingStatus(str, enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    NO_SHOW = 'no_show'

class Booking(BaseModel):
    __tablename__ = 'bookings'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    venue_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('venues.id', ondelete='CASCADE'), nullable=False, index=True)
    service_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('services.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('resources.id', ondelete='CASCADE'), nullable=False, index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus, name='booking_status'), nullable=False, default=BookingStatus.CONFIRMED, index=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    recurrence_group_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)

    user: Mapped['User'] = relationship(back_populates='bookings', lazy='noload')
    venue: Mapped['Venue'] = relationship(back_populates='bookings', lazy='noload')
    service: Mapped['Service'] = relationship(back_populates='bookings', lazy='noload')
    resource: Mapped['Resource'] = relationship(back_populates='bookings', lazy='noload')
    review: Mapped['Review | None'] = relationship(back_populates='booking', lazy='noload', uselist=False)

    __table_args__ = (
        Index('idx_bookings_user_id', 'user_id'),
        Index('idx_bookings_venue_id', 'venue_id'),
        Index('idx_bookings_resource_id', 'resource_id'),
        Index('idx_bookings_starts_at', 'starts_at'),
        Index('idx_bookings_status', 'status'),
        Index('idx_bookings_recurrence_group', 'recurrence_group_id'),
    )

BOOKING_EXCLUSION_CONSTRAINT_DDL = DDL(
    """
    ALTER TABLE bookings
    ADD CONSTRAINT booking_no_overlap
    EXCLUDE USING gist (
        resource_id WITH =,
        tstzrange(starts_at, ends_at) WITH &&
    )
    WHERE (status IN ('pending', 'confirmed'));
    """
)

DROP_BOOKING_EXCLUSION_CONSTRAINT_DDL = DDL(
    "ALTER TABLE bookings DROP CONSTRAINT IF EXISTS booking_no_overlap"
)