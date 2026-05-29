from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db, AdminUser
from app.schemas.auth import (
    PasswordChangeRequest,
    UserBlockRequest,
    UserResponse,
    UserRoleUpdateRequest,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix='/users', tags=['users'])
DB = Annotated[AsyncSession, Depends(get_db)]

@router.get('/me', response_model=UserResponse, summary='Get current user profile')
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)

@router.patch('/me', response_model=UserResponse, summary='Update current user profile')
async def update_me(payload: UserUpdateRequest, current_user: CurrentUser, db: DB) -> UserResponse:
    svc = UserService(db)
    user = await svc.update_profile(current_user, payload)
    await db.commit()
    return UserResponse.model_validate(user)

@router.post('/me/change-password', status_code=status.HTTP_204_NO_CONTENT, summary='Change current user password (invalidates all sessions)')
async def change_password(payload: PasswordChangeRequest, current_user: CurrentUser, db: DB):
    svc = UserService(db)
    await svc.change_password(current_user, payload)
    await db.commit()

@router.get('/{user.id}', response_model=UserResponse, summary='[Admin] Get any user by ID')
async def admin_get_user(user_id: UUID, _admin: AdminUser, db: DB) -> UserResponse:
    svc = UserService(db)
    user = await svc.get_by_id(user_id)
    return UserResponse.model_validate(user)

@router.patch('/{user.id}/role', response_model=UserResponse, summary='[Admin] Change user role')
async def admin_set_role(user_id: UUID, payload: UserRoleUpdateRequest, admin: AdminUser, db: DB) -> UserResponse:
    svc = UserService(db)
    user = await svc.admin_set_role(admin, user_id, payload)
    await db.commit()
    return UserResponse.model_validate(user)

@router.patch('/{user.id}/block', response_model=UserResponse, summary='[Admin] Blok or unblock a user')
async def admin_block_user(user_id: UUID, payload: UserBlockRequest, admin: AdminUser, db: DB) -> UserResponse:
    svc = UserService