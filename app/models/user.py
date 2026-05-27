import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Index, String, Text
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC

from app.db.base import BaseModel

from app.models.venue import Venue
from app.models.booking import Booking
from app.models.waitlist import WaitlistEntry
from app.models.notification import NotificationEvent
from app.models.review import Review

class UserRole(str, enum.Enum):
    USER = 'user'
    VENUE_OWNER = 'venue_owner'
    ADMIN = 'admin'

class User(BaseModel):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name='user_role'), nullable=False, default=UserRole.USER, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    refresh_tokens: Mapped[list['RefreshToken']] = relationship(back_populates='user', cascade='all, delete-orphan', lazy='noload')
    venus: Mapped[list['Venue']] = relationship(back_populates='owner', lazy='noload')
    bookings: Mapped[list['Booking']] = relationship(back_populates='user', lazy='noload')
    waitlist_entries: Mapped[list['WaitlistEntry']] = relationship(back_populates='user', lazy='noload')
    notifications: Mapped[list['NotificationEvent']] = relationship(back_populates='user', lazy='noload')
    reviews: Mapped[list['Review']] = relationship(back_populates='user', lazy='noload')

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_role', 'role'),
    )

    def __repr__(self) -> str:
        return f'<User {self.username} ({self.email})>'
    
class RefreshToken(BaseModel):
    __tablename__ = 'refresh_tokens'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(INET)

    user: Mapped['User'] = relationship(back_populates='refresh_tokens', lazy='noload')

    @property
    def is_valid(self) -> bool:
        return self.revoked_at is None and self.expires_at > datetime.now(UTC)