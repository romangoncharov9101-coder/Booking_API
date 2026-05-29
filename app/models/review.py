import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text, 
    UniqueConstraint,
    Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.venue import Venue
    from app.models.booking import Booking

class Review(BaseModel):
    __tablename__ = 'reviews'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    venue_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('venues.id', ondelete='CASCADE'), nullable=False, index=True)
    booking_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False, unique=True)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped['User'] = relationship(back_populates='reviews', lazy='noload')
    venue: Mapped['Venue'] = relationship(back_populates='reviews', lazy='noload')
    booking: Mapped['Booking'] = relationship(back_populates='review', lazy='noload')

    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='ck_reviews_rating'),
        UniqueConstraint('user_id', 'booking_id', name='uq_review_user_booking'),
        Index('idx_reviews_venue_id', 'venue_id'),
        Index('idx_reviews_user_id', 'user_id'),
    )