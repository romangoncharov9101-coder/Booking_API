import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from app.core.config import settings
from app.core.exceptions import TokenExpiredError, TokenInvalidError

pwd_context = CryptContext(schemas=['argon2', 'bcrypt'], deprecated='auto')

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def _create_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    payload['exp'] = expire
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_access_token(user_id: UUID, email: str, username: str, role: str) -> str:
    return _create_token(
        {
            'sub': str(user_id),
            'email': email,
            'username': username,
            'role': role,
            'type': 'access',
        },
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

def create_refresh_token(user_id: UUID, jti: str) -> str:
    return _create_token(
        {
            'sub': str(user_id),
            'type': 'refresh',
            'jti': jti,
        },
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

def decode_token(token: str, type: str) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise TokenInvalidError()
    
    if payload.get('type') != type:
        raise TokenInvalidError
    return payload

def generate_jti() -> str:
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def refresh_token_expires_at() -> datetime:
    return datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)