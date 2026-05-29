from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsError,
    PermissionDeniedError,
    UserNotFoundError,
)
from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.schemas.auth import (
    PasswordChangeRequest,
    UserBlockRequest,
    UserRoleUpdateRequest,
    UserUpdateRequest,
)

logger = get_logger(__name__)

class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._tokens = RefreshTokenRepository(db)

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
    
    async def update_profile(self, user: User, payload: UserUpdateRequest) -> User:
        data = payload.model_dump(exclude_none=True)
        if not data:
            return user
        return await self._users.update_fields(user, **data)
    
    async def change_password(self, user: User, payload: PasswordChangeRequest) -> None:
        if not verify_password(payload.current_password, user.password_hash):
            raise InvalidCredentialsError('Current password is incorrect.')
        new_hash = hash_password(payload.new_password)
        await self._users.update_fields(user, password_hash=new_hash)
        await self._tokens.revoke_all_for_user(user.id)

    async def admin_set_role(self, actor: User, target_user_id: UUID, payload: UserRoleUpdateRequest) -> User:
        if actor.role != UserRole.ADMIN:
            raise PermissionDeniedError()
        
        target = await self.get_by_id(target_user_id)
        if actor.id == target.id and payload.role != UserRole.ADMIN:
            raise PermissionDeniedError('Cannot change your own admin role.')
        
        updated = await self._users.set_role(target, payload.role)
        return updated
    
    async def admin_set_active(self, actor: User, target_user_id: UUID, payload: UserBlockRequest):
        if actor.role != UserRole.ADMIN:
            raise PermissionDeniedError()
        
        target = await self.get_by_id(target_user_id)
        if actor.id == target.id:
            raise PermissionDeniedError('Cannot block your own account.')
        
        updated = await self._users.set_active(target, is_active=payload.is_active)
        if not payload.is_active:
            await self._tokens.revoke_all_for_user(target.id)
        return updated