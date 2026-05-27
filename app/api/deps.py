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
from app.models.user import User, UserRoel