from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    TokenRevokeError,
    UserEmailAlreadyExistsError,
    UserInactiveError,
    UsernameAlreadyExistsError,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_jti,
    hash_password, 
    hash_token,
    refresh_token_expires_at,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

logger = get_logger(__name__)

class AuthService:
    """
    Handles registration, login, token refresh and logout.

    Every method works within the caller`s transaction - the router/endpoint
    is responsible for calling db.commit() on success.
    """
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._tokens = RefreshTokenRepository(db)

    async def register(self, payload: RegisterRequest) -> User:
        # Check uniqueness - give specific errors so the client knows which field failed
        if await self._users.email_exists(payload.email):
            raise UserEmailAlreadyExistsError()
        if await self._users.username_exists(payload.username):
            raise UsernameAlreadyExistsError()
        
        user = await self._users.create(
            email=payload.email,
            username=payload.username,
            password_hash=hash_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        return user
    
    async def login(
            self,
            payload: LoginRequest,
            *,
            user_agent: str | None = None,
            ip_address: str | None = None,
    ) -> TokenResponse:
        user = await self._users.get_by_login(payload.login)
        dummy_hash = '$argon2id$v=19$m=65536,t=3,p=4$placeholder'
        candidate_hash = user.password_hash if user else dummy_hash

        if not verify_password(payload.password, candidate_hash) or user is None:
            raise InvalidCredentialsError()
        if not user.is_active:
            raise UserInactiveError()
        
        return await self._issue_token_pair(user, user_agent=user_agent, ip_address=ip_address)
    
    async def refresh(
            self,
            raw_refresh_token: str,
            *, 
            user_agent: str | None = None,
            ip_address: str | None = None,
    ) -> TokenResponse:
        try:
            payload = decode_token(raw_refresh_token, 'refresh')
        except (TokenExpiredError, TokenInvalidError):
            raise

        stored = await self._tokens.get_by_hash(hash_token(raw_refresh_token))
        if stored is None:
            raise TokenInvalidError()
        
        if stored.revoked_at is not None:
            logger.warning('refresh_token_reuse_detected', user_id=str(stored.user_id))
            await self._tokens.revoke_all_for_user(stored.user_id)
            raise TokenRevokeError()
        
        if stored.expires_at < datetime.now(UTC):
            raise TokenExpiredError()
        user = await self._users.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            raise InvalidCredentialsError()
        await self._tokens.revoke(stored)
        return await self._issue_token_pair(user, user_agent=user_agent, ip_address=ip_address)
    
    async def logout(self, raw_refresh_token: str) -> None:
        stored = await self._tokens.get_by_hash(hash_token(raw_refresh_token))
        if stored and stored.revoked_at is None:
            await self._tokens.revoke(stored)

    async def logout_all(self, user_id: UUID) -> None:
        await self._tokens.revoke_all_for_user(user_id)
    
    async def _issue_token_pair(
            self,
            user: User,
            *,
            user_agent: str | None,
            ip_address: str | None,
    ) -> TokenResponse:
        jti = generate_jti()
        raw_refresh = create_refresh_token(user.id, jti)
        raw_access = create_access_token(user.id, user.email, user.username, user.role.value)
        await self._tokens.create(
            user_id=user.id,
            token_hash=hash_token(raw_refresh),
            expires_at=refresh_token_expires_at(),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return TokenResponse(access_token=raw_access, refresh_token=raw_refresh)