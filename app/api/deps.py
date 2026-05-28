from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    PermissionDeniedError,
    TokenInvalidError,
    UserInactiveError,
    UserNotFoundError,
)
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={'code': 'AUTH_MISSING_TOKEN', 'message': 'Authentication required.'},
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    try:
        payload = decode_access_token(credentials.credentials)
    except TokenInvalidError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={'code': e.error_code, 'message': e.message},
            headers={'WWW-Authenticated': 'Bearer'}
        )
    user_id: str | None = payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={'code': 'USER_INACTIVE', 'message': 'User account is inactive.'}
        )
    return user

async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User | None:
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
    
def require_role(*roles: UserRole):
    async def _check(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={'code': 'PERMISSIONS_DENIED', 'message': 'insufficient permissions.'}
            )
        return current_user
    return _check

require_admin = require_role(UserRole.ADMIN)
require_venue_owner = require_role(UserRole.VENUE_OWNER, UserRole.ADMIN)
require_authenticated = get_current_user

CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]
AdminUser = Annotated[User, Depends(require_role(UserRole.ADMIN))]
VenueOwnerUser = Annotated[User, Depends(require_role(UserRole.VENUE_OWNER, UserRole.ADMIN))]