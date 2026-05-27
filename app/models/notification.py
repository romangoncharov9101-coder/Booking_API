import enum
import uuid
from datetime import time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.models.user import User
from app.models.booking import Booking
from app.models.waitlist import WaitlistEntry
from app.models.review import Review

class ResourceType(str, enum.Enum):
    STAFF = 'staff'
    ROOM = 'room'
    TABLE = 'table'
    EQUIPMENT = 'equipment'
    OTHER = 'other'

class ScheduleExceptionType(str, enum.Enum):
    CLOSED = 'closed'
    AVAILABLE = 'available'
    BLOCKED = 'blocked'

class Venue(BaseModel):
    __tablename__ = 'venues'

    ownre_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default='UTC')
    phone: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    owner: Mapped['User'] = relationship(back_populates='venues', lazy='noload')
    services: Mapped[list['Service']] = relationship(back_populates='venue', cascade='all, delete-orphan', lazy='noload')
    resources: Mapped[list['Resource']] = relationship(back_populates='venue', cascade='all, delete-orphan', lazy='noload')
    working_hours: Mapped[list['VenueWorkingHours']] = relationship(back_populates='venue', cascade='all, delete-orphan', lazy='noload')
    schedule_exceptions: Mapped[list['ScheduleException']] = relationship(back_populates='venue', cascade='all, delete-orphan', lazy='noload')
    bookings: Mapped[list['Bookings']] = relationship(back_populates='venue', lazy='noload')
    waitlist_entries: Mapped[list['WaitlistEntry']] = relationship(back_populates='venue', lazy='noload')
    reviews: Mapped[list['Review']] = relationship(back_populates='venue', lazy='noload')

    __table_args__ = (
        Index('idx_venues_owner_id', 'owner_id'),
        Index('idx_venues_slug', 'slug'),
        Index('idx_venues_city', 'city'),
        Index('idx_venues_is_active', 'is_active'),
    )

class Service(BaseModel):
    __tablename__ = 'services'

    venue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('venues.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='EUR')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    venue: Mapped['Venue'] = relationship(back_populates='services', lazy='noload')
    service_resources: Mapped[list['ServiceResource']] = relationship(back_populates='service', cascade='all, delete-orphan', lazy='noload')
    bookings: Mapped[list[Booking]] = relationship(back_populates='service', lazy='noload')

    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='ck_service_duration_positive'),
        CheckConstraint('price >= 0', name='ck_service_price_non_negative'),
        Index('idx_service_venue_id', 'venue_id'),
    )
    