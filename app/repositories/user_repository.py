from datetime import UTC, datetime
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RefreshToken, UserRole, User

class UserRepository:
    """Pure data-accesss layer for users. No business logic here."""
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self._db.execute(select(User).where(User.email == email.lower().strip()))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> User | None:
        result = await self._db.execute(select(User).where(User.username == username.strip()))
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str) -> User | None:
        result = await self._db.execute(select(User).where((User.email == login.lower().strip()) | (User.username == login.strip())))
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str) -> bool:
        result = await self._db.execute(select(User.id).where(User.email == email.lower().strip()))
        return result.scalar_one_or_none() is not None
    
    async def username_exists(self, username: str) -> bool:
        result = await self._db.execute(select(User.id).where(User.username == username.strip()))
        return result.scalar_one_or_none() is not None
    

    async def create(
            self,
            *,
            email: str,
            username: str,
            password_hash: str,
            first_name: str | None = None,
            last_name: str | None = None,
            role: UserRole = UserRole.USER,
    ) -> User:
        user = User(
            email=email.lower().strip(),
            username=username.strip(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        self._db.add(user)
        await self._db.refresh(user)
        return user
    
    async def update_fields(self, user: User, **kwargs: object) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user
    
    async def set_role(self, user: User, role: UserRole) -> User:
        return await self.update_fields(user, role=role)
    
    async def set_active(self, user: User, *, is_active: bool) -> User:
        return await self.update_fields(user, is_active=is_active)
    
class RefreshTokenRepository:
    """Data-access layer for refresh tokens."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
            self, 
            *,
            user_id: UUID,
            token_hash: str,
            expires_at: datetime,
            user_agent: str | None = None,
            ip_address: str | None = None,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self._db.add(token)
        await self._db.flush()
        return token
    
    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self._db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        return result.scalar_one_or_none()
    
    async def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(UTC)
        self._db.add(token)
        await self._db.flush()

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        await self._db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
    
