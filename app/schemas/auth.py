import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.user import UserRole

PASSWORD_MIN_LENGTH = 8
_PASSWORD_RE = re.compile(r'^(?=.*[A-Za-z])(?=.*\d).+$')
_USERNAME_RE = re.compile(r'^[a-zA-Z0-9_.-]+$')

def validate_password_strength(v : str) -> str:
    if len(v) < PASSWORD_MIN_LENGTH:
        raise ValueError(f'Password must be at least {PASSWORD_MIN_LENGTH} characters.')
    if not _PASSWORD_RE.match(v):
        raise ValueError('Password must contain at least one letter and one digit.')
    return v

def validate_username_format(v: str) -> str:
    if not _USERNAME_RE.match(v):
        raise ValueError('Username may only letters, underscores, dots and hyphens.')
    return v

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_password_strength(v)
    
    @field_validator('username')
    @classmethod
    def username_format(cls, v: str) -> str:
        return validate_username_format(v.strip())
    
    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower().strip()
    
class LoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=255, description='Email or username')
    password: str = Field(min_length=1, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    first_name: str | None
    last_name: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {'from_attributes': True}

class UserPublicResponse(BaseModel):
    id: UUID
    username: str
    first_name: str | None
    last_name: str | None

    model_config = {'from_attributes': True}

class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=100)
    username: str | None = Field(default=None, max_length=100)

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=3, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator('new_password')
    @classmethod
    def new_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)
    
    @model_validator(mode='after')
    def password_differ(self) -> 'PasswordChangeRequest':
        if self.current_password == self.new_password:
            raise ValueError('New password must differ from the current password.')
        return self
    
class UserRoleUpdateRequest(BaseModel):
    role: UserRole

class UserBlockRequest(BaseModel):
    is_active: bool
    reason: str | None = Field(default=None, max_length=500)